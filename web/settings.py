from typing import Tuple
from enum import Enum
from functools import lru_cache
from pydantic import BaseSettings, SecretStr, PostgresDsn


class E_PGDriver(str, Enum):
    psycopg2 = "psycopg2"
    pg8000 = "pg8000"
    asyncpg = "asyncpg"
    psycopg2cffi = "psycopg2cffi"


class _Settings(BaseSettings):
    secret_key: SecretStr
    csrf_secret_key: SecretStr
    max_age: int = 3600
    hosts: Tuple[str, ...] = ("localhost", "127.0.0.1")
    origins: Tuple[str, ...] = tuple()
    origin_regex: str = r"^http://(localhost|127.0.0.1)(:\d{2,5})?$"
    http_meothds: Tuple[str, ...] = ("GET", "OPTIONS", "POST")
    sql_db_driver: E_PGDriver = E_PGDriver.psycopg2
    sql_db_url: PostgresDsn

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return _Settings()
