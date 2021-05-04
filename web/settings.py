from typing import Tuple
from functools import lru_cache
from pydantic import BaseSettings, SecretStr, BaseModel, PostgresDsn


class _Settings(BaseSettings):
    secret_key: SecretStr
    csrf_secret_key: SecretStr
    max_age: int = 3600
    hosts: Tuple[str, ...] = ("localhost", "127.0.0.1")
    origins: Tuple[str, ...] = tuple()
    origin_regex: str = r"^http://(localhost|127.0.0.1)(:\d{2,5})?$"
    http_meothds: Tuple[str, ...] = ("GET", "OPTIONS", "POST")
    # sql_db_url:PostgresDsn

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return _Settings()


class StringConstraint(BaseModel):
    min_length: int = None
    max_length: int = None
    regex: str = None


class _Constraints(BaseSettings):
    user_id: StringConstraint = StringConstraint(
        min_length=4, max_length=32, regex=r"^[a-zA-Z]([_-]?[a-zA-Z0-9]+)+$"
    )
    password: StringConstraint = StringConstraint(
        min_length=8, regex=r"^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9@#$%^&+=*._-]){8,}$"
    )


@lru_cache()
def constraints():
    return _Constraints()
