import os
import pytest
from httpx import AsyncClient
from contextlib import contextmanager
from sqlalchemy_utils import drop_database
from web.sql.orm import orm_metadata
from web.settings import get_settings
from web.schema.member import SignUpForm, SignInForm
from web.csrf import DEFAULT_CSRF_NS


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


@pytest.fixture()
def async_client():
    from web.main import app  # avoid missing value errors when loading settings

    # See `settings.origin_regex` and `settings.hosts`
    origin = "http://localhost"
    return AsyncClient(app=app, base_url=origin, headers={"origin": origin})


@pytest.fixture()
def testing_sql_db_contextmanager():
    from web.sql.core import init_db, close_db

    class CM:
        def __enter__(self):
            metadata = orm_metadata()
            init_db(metadata)

        def __exit__(self, exc_type, exc_val, exc_tb):
            drop_database(get_settings().sql_db_url)
            close_db()

    return CM


@pytest.fixture()
def db_session_generator():
    from web.sql.core import db_session  # avoid missing value errors when loading settings

    return contextmanager(db_session)


@pytest.fixture()
def raw_sign_up_from_data():
    return dict(
        user_id="aB-c0_ef1",
        email="contact@testing.com",
        password="0z12@3456",
        password_confirm="0z12@3456",
    )


@pytest.fixture()
def raw_sign_in_from_data():
    return dict(
        email="contact@testing.com",
        password="0z12@3456",
    )


@pytest.fixture()
def demo_sign_in_form():
    return SignInForm(
        email="contact@demo-member.com",
        password="demo@678",
    )


@pytest.fixture()
def demo_sign_up_form():
    return SignUpForm(
        user_id="demo-member",
        email="contact@demo-member.com",
        password="demo@678",
        password_confirm="demo@678",
    )


@pytest.fixture()
def demo_member_profile():
    return dict(
        display_name="Demo Member",
        intro=(
            "Pellentesque ut venenatis orci, sed egestas arcu."
            " Vivamus finibus luctus rhoncus. Nunc lacinia interdum nibh,"
            " sed sollicitudin nulla imperdiet vel."
            " Etiam sed libero at mauris tristique faucibus ac a mauris."
            " Aenean consequat eget lacus eget congue placerat."
        ),
    )


@pytest.fixture()
def async_mock_browse_form():
    async def fn(url: str, async_client: AsyncClient, headers: dict, form_data: dict):
        # fetch csrf token
        resp = await async_client.get(url)

        for line in resp.iter_lines():
            l = line.strip()
            flag = 'name="form-csrf-token" value='
            pos = l.find(flag)
            if pos > 0:
                token = l[pos + len(flag) :].strip('">')
                form_data[DEFAULT_CSRF_NS] = token
                break
        # mock `referer` header
        headers.setdefault("referer", str(async_client.base_url.join(url)))

    return fn
