from functools import lru_cache
from pydantic import BaseSettings, SecretStr


class _Settings(BaseSettings):
    secret_key: SecretStr

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return _Settings()
