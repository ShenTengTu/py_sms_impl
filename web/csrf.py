import os
import hashlib
import hmac
from functools import lru_cache
from urllib.parse import urlparse, ParseResult
from starlette.datastructures import URL
from fastapi import Request, HTTPException
from itsdangerous import URLSafeTimedSerializer, BadData, SignatureExpired
from .settings import get_settings


def _token_digest():
    return hashlib.blake2b(os.urandom(64)).hexdigest()


def _crsf_token(secret_key: str, token_digest: str, namespace: str):
    return URLSafeTimedSerializer(secret_key, salt=namespace).dumps(token_digest)


def _load_crsf_token(secret_key: str, data: str, namespace: str, time_limit: int):
    return URLSafeTimedSerializer(secret_key, salt=namespace).loads(
        data, max_age=time_limit
    )


def setup_crsf(request: Request, secret_key: str, namespace: str):
    session = request.session
    if namespace not in session:
        session[namespace] = _token_digest()
    return _crsf_token(secret_key, session[namespace], namespace)


class CSRFTokenExpired(HTTPException):
    def __init__(self, message: str):
        super(HTTPException, self).__init__(400, detail=message)


class _CSRFValidator:
    """FastAPI dependency class for verifying CSRF Token."""

    @staticmethod
    def _verify_origin(src: ParseResult, target: URL, host=False):
        result = src.hostname == target.hostname and src.port == target.port
        if not host:
            result = result and (src.scheme == target.scheme)
        return result

    def __init__(self, namespace: str, time_limit: int):
        self.namespace = namespace
        self.time_limit = time_limit
        self.secret_key = get_settings().secret_key

    async def __call__(self, request: Request):
        headers = request.headers
        url = request.url

        # Verify origin
        host = headers.get("host")
        if host:
            if not self._verify_origin(urlparse("//%s" % host), url, host=True):
                raise HTTPException(
                    status_code=403, detail="The request isn't from the same origin."
                )

        host = headers.get("x-forwarded-host")
        if host:
            if not self._verify_origin(urlparse("//%s" % host), url, host=True):
                raise HTTPException(
                    status_code=403, detail="The request isn't from the same origin."
                )

        origin = headers.get("origin")
        if not origin:
            raise HTTPException(status_code=400, detail="Header `origin` is missing.")
        if not self._verify_origin(urlparse(origin), url):
            raise HTTPException(
                status_code=403, detail="The request isn't from the same origin."
            )

        referer = headers.get("referer")
        if not referer:
            raise HTTPException(status_code=400, detail="Header `referer` is missing.")
        if not self._verify_origin(urlparse(referer), url):
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

        try:
            raw_token = _load_crsf_token(
                self.secret_key.get_secret_value(), token, self.namespace, self.time_limit
            )
        except SignatureExpired:
            raise CSRFTokenExpired("The CSRF token has expired.")
        except BadData:
            HTTPException(status_code=400, detail="The CSRF token is invalid.")

        if not hmac.compare_digest(request.session[self.namespace], raw_token):
            raise HTTPException(status_code=400, detail="The CSRF token is invalid.")

        return request


@lru_cache()
def csrf_validator(namespace: str = "form-csrf-token", time_limit: int = 14 * 24 * 60 * 60):
    return _CSRFValidator(namespace, time_limit)
