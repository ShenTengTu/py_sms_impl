from web.settings import get_settings
from web.csrf import crsf_serializer, csrf_provider, csrf_validator


def test_lru_cache():
    s1 = get_settings()
    s2 = get_settings()
    assert id(s1) == id(s2)

    ns = "form-csrf-token"
    cs1 = crsf_serializer(s1.secret_key.get_secret_value(), ns)
    cs2 = crsf_serializer(s2.secret_key.get_secret_value(), ns)
    assert id(cs1) == id(cs2)

    cp1 = csrf_provider()
    cp2 = csrf_provider()
    assert id(cp1) == id(cp2)

    cv1 = csrf_validator(time_limit=s1.max_age)
    cv2 = csrf_validator(time_limit=s2.max_age)
    assert id(cv1) == id(cv2)
