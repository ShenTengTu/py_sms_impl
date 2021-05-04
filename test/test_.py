# This file must be the first order of testing
from web.settings import get_settings
from web.crypto import crypt_context, crypt_hash, crypt_verify


def test_setting():
    settings = get_settings()
    assert settings.secret_key.get_secret_value() == "test_secret_key"
    assert settings.csrf_secret_key.get_secret_value() == "test_csrf_secret_key"
    assert settings.max_age == 600


def test_crypt():
    assert id(crypt_context()) == id(crypt_context())
    p = "test_secret"
    assert crypt_verify(p, crypt_hash(p))
    assert not crypt_verify(p.capitalize(), crypt_hash(p))
