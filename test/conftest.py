import pytest
from httpx import AsyncClient


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    # mock environment variables, overide values in `.env` file
    monkeypatch.setenv("SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("CSRF_SECRET_KEY", "test_csrf_secret_key")
    monkeypatch.setenv("MAX_AGE", "600")


@pytest.fixture(scope="module")
def async_client():
    from web.main import app  # avoid missing value errors when loading settings

    # See `settings.origin_regex` and `settings.hosts`
    origin = "http://localhost"
    return AsyncClient(app=app, base_url=origin, headers={"origin": origin})
