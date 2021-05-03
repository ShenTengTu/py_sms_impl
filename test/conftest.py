import pytest
from httpx import AsyncClient
from web.main import app
from web.csrf import DEFAULT_CSRF_NS


@pytest.fixture(scope="module")
def async_client():
    # See `settings.origin_regex` and `settings.hosts`
    origin = "http://localhost"
    return AsyncClient(app=app, base_url=origin, headers={"origin": origin})
