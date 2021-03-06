import os
import hashlib
import hmac
from functools import lru_cache
from urllib.parse import urlparse
from fastapi import Request, HTTPException
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from .settings import get_settings

DEFAULT_CSRF_NS = "form-csrf-token"


def _token_digest():
    return hashlib.blake2b(os.urandom(64)).hexdigest()


@lru_cache()
def crsf_serializer(secret_key: str, namespace: str):
    return URLSafeTimedSerializer(secret_key, salt=namespace)


def _crsf_token(secret_key: str, token_digest: str, namespace: str):
    return crsf_serializer(secret_key, namespace).dumps(token_digest)


def _load_crsf_token(secret_key: str, data: str, namespace: str, time_limit: int):
    return crsf_serializer(secret_key, namespace).loads(data, max_age=time_limit)


def setup_crsf(request: Request, secret_key: str, namespace: str):
    session = request.session
    if namespace not in session:
        session[namespace] = _token_digest()
    return _crsf_token(secret_key, session[namespace], namespace)


class CSRFTokenExpired(HTTPException):
    def __init__(self, message: str):
        super(HTTPException, self).__init__(400, detail=message)


class BadCSRFToken(HTTPException):
    def __init__(self, message: str):
        super(HTTPException, self).__init__(400, detail=message)


def verify_crsf(
    request: Request, secret_key: str, token: str, namespace: str, time_limit: int
):
    try:
        raw_token = _load_crsf_token(secret_key, token, namespace, time_limit)
    except SignatureExpired:
        raise CSRFTokenExpired("The CSRF token has expired.")
    except BadSignature:
        raise BadCSRFToken("The CSRF token is invalid.")

    if not hmac.compare_digest(request.session[namespace], raw_token):
        raise BadCSRFToken("The CSRF token is invalid.")


class _CSRFProvider:
    """FastAPI dependency class for providing CSRF Token."""

    def __init__(self, namespace: str):
        self.namespace = namespace
        self.secret_key = get_settings().csrf_secret_key

    async def __call__(self, request: Request):
        ns = self.namespace
        token = setup_crsf(request, self.secret_key.get_secret_value(), ns)
        return (ns, token)


class _CSRFValidator:
    """FastAPI dependency class for verifying CSRF Token."""

    @staticmethod
    def _verify_origin(src_url: str, target_url: str):
        try:
            src = urlparse(src_url)
            target = urlparse(target_url)
            result = (
                src.scheme == target.scheme
                and src.hostname == target.hostname
                and src.port == target.port
            )
            return result
        except ValueError:
            raise False

    def __init__(self, namespace: str, time_limit: int):
        self.namespace = namespace
        self.time_limit = time_limit

        setting = get_settings()
        self.secret_key = setting.csrf_secret_key
        self.allowed_hosts = setting.hosts

    async def __call__(self, request: Request):
        headers = request.headers
        url = request.url

        # Verify host
        host = headers.get("x-forwarded-host", headers.get("host"))
        if not host:
            host = host = "%s:%s" % request.scope["server"]
        allowed_hosts = self.allowed_hosts
        is_valid_host = "*" in allowed_hosts
        if not is_valid_host:
            for pattern in allowed_hosts:
                if host == pattern:
                    is_valid_host = True
                    break
                if pattern.startswith("*") and host.endswith(pattern[1:]):
                    is_valid_host = True
                    break
        if not is_valid_host:
            raise HTTPException(status_code=403, detail="Invalid host.")

        # Verify origin
        origin = headers.get("origin")
        if not origin:
            raise HTTPException(status_code=400, detail="Header `origin` is missing.")
        scheme = "https" if request.scope["scheme"] == "https" else "http"
        valid_origin = "%s://%s" % (scheme, host)
        if not self._verify_origin(origin, valid_origin):
            raise HTTPException(status_code=403, detail="Invalid origin.")

        # Verify referer
        referer = headers.get("referer")
        if not referer:
            raise HTTPException(status_code=400, detail="Header `referer` is missing.")
        if not self._verify_origin(referer, valid_origin):
            raise HTTPException(
                status_code=403, detail="The request isn't from the same origin."
            )

        # Verify token
        form_data = await request.form()
        token = form_data.get(self.namespace)
        if not token:
            token = request.headers.get("x-csrf-token")
        if not token:
            raise HTTPException(status_code=400, detail="The CSRF token is missing.")

        verify_crsf(
            request,
            self.secret_key.get_secret_value(),
            token,
            self.namespace,
            self.time_limit,
        )

        return request


@lru_cache()
def csrf_provider(namespace: str = DEFAULT_CSRF_NS):
    return _CSRFProvider(namespace)


@lru_cache()
def csrf_validator(namespace: str = DEFAULT_CSRF_NS, time_limit: int = 14 * 24 * 60 * 60):
    return _CSRFValidator(namespace, time_limit)
