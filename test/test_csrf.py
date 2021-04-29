import pytest
from time import sleep
from web.settings import get_settings
from web.csrf import (
    setup_crsf,
    verify_crsf,
    CSRFTokenExpired,
    BadCSRFToken,
    DEFAULT_CSRF_NS,
)


class FakeRequest:
    def __init__(self):
        self.session = {}

    def clear_session(self):
        self.session = {}


def test_csrf():
    setting = get_settings()

    req = FakeRequest()
    secret_key = setting.secret_key.get_secret_value()
    time_limit = 1

    # expired token
    token = setup_crsf(req, secret_key, DEFAULT_CSRF_NS)
    with pytest.raises(CSRFTokenExpired):
        sleep(2)
        verify_crsf(req, secret_key, token, DEFAULT_CSRF_NS, time_limit)

    req.clear_session()

    # bad token (not match)
    token = setup_crsf(req, secret_key, DEFAULT_CSRF_NS)
    req.clear_session()
    setup_crsf(req, secret_key, DEFAULT_CSRF_NS)
    with pytest.raises(BadCSRFToken):
        verify_crsf(req, secret_key, token, DEFAULT_CSRF_NS, time_limit)

    req.clear_session()

    # bad token (wrong format)
    token = setup_crsf(req, secret_key, DEFAULT_CSRF_NS)
    token = token.replace(".", "-")
    with pytest.raises(BadCSRFToken):
        verify_crsf(req, secret_key, token, DEFAULT_CSRF_NS, time_limit)

    req.clear_session()

    # valid token
    token = setup_crsf(req, secret_key, DEFAULT_CSRF_NS)
    verify_crsf(req, secret_key, token, DEFAULT_CSRF_NS, time_limit)
