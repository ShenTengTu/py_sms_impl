import os
import hashlib
from fastapi import Request
from itsdangerous import URLSafeTimedSerializer


def _token_digest():
    return hashlib.blake2b(os.urandom(64)).hexdigest()


def _crsf_token(secret_key: str, token_digest: str, namespace: str):
    return URLSafeTimedSerializer(secret_key, salt=namespace).dumps(token_digest)


def setup_crsf(request: Request, secret_key: str, namespace: str):
    session = request.session
    if namespace not in session:
        session[namespace] = _token_digest()
    return _crsf_token(secret_key, session[namespace], namespace)
