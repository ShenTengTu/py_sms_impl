import os
import pytest
from httpx import AsyncClient
from sqlalchemy_utils import drop_database
from web.sql.orm import orm_metadata
from web.settings import get_settings


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    # mock environment variables, overide values in `.env` file
    monkeypatch.setenv("SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("CSRF_SECRET_KEY", "test_csrf_secret_key")
    monkeypatch.setenv("MAX_AGE", "600")
    SQL_DB_PASSWORD = os.environ["SQL_DB_PASSWORD"]
    SQL_DB_HOST = os.environ["SQL_DB_HOST"]
    SQL_DB_NAME = os.environ["SQL_DB_NAME"]
    monkeypatch.setenv(
        "SQL_DB_URL",
        f"postgresql://postgres:{SQL_DB_PASSWORD}@{SQL_DB_HOST}:5432/{SQL_DB_NAME}",
    )


@pytest.fixture(scope="module")
def async_client():
    from web.main import app  # avoid missing value errors when loading settings

    # See `settings.origin_regex` and `settings.hosts`
    origin = "http://localhost"
    return AsyncClient(app=app, base_url=origin, headers={"origin": origin})


@pytest.fixture()
def init_sql_db():

    from web.sql.core import init_db

    def fn():
        metadata = orm_metadata()
        init_db(metadata)

    return fn


@pytest.fixture()
def drop_sql_db():
    def fn():
        drop_database(get_settings().sql_db_url)

    return fn


@pytest.fixture()
def db_session_generator():
    from web.sql.core import db_session  # avoid missing value errors when loading settings

    return db_session
