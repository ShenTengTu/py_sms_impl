from functools import lru_cache
from passlib.context import CryptContext


@lru_cache()
def crypt_context():
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


def crypt_hash(secret: str):
    return crypt_context().hash(secret)


def crypt_verify(secret: str, hash: str):
    return crypt_context().verify(secret, hash)
