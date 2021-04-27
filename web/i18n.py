from pathlib import Path
from babel.core import Locale
from babel.support import Translations, NullTranslations
from . import path_locale


_translations_dict = {None: NullTranslations()}
_fallback_ns = "_fallback"


def load_translations(*locales: str, domain=None):
    """Loads all translation of locales, fallback translation is first locale"""
    loc_ins = None
    for loc in reversed(locales):
        try:
            loc_ins = Locale.parse(loc)
        except:
            continue
        _translations_dict[loc_ins] = Translations.load(path_locale, loc_ins, domain)
    _translations_dict[_fallback_ns] = _translations_dict[loc_ins]


def get_translation(locale: str = _fallback_ns) -> Translations:
    """Gets  the loaded translation by locale.

    If nothing matches, return fallback translation or null translation.
    """
    null_trans = _translations_dict[None]
    try:
        locale = Locale.parse(locale)
    except:
        if locale is None:
            return null_trans
        if not locale == _fallback_ns:
            locale = _fallback_ns
    return _translations_dict.get(locale, null_trans)


def is_babel_translation(translation):
    """Returns true if the object is an instance of `babel.support.Translations`"""
    return isinstance(translation, Translations)


def parse_accept_language(data: str = None):
    """Parse HTTP header `Accept-Language`

    Returns a tuple like below:
    ```
    ((1.0, Locale('zh_Hant_TW')), (0.9, Locale('en')), (0.0,  _fallback_ns))
    ```
    """
    langs = {(0.0, _fallback_ns)}
    if data is None:
        return tuple(langs)

    for s in data.split(","):
        tags = s.strip().split(";")
        loc_ins = Locale.parse(tags[0], sep="-")
        q = 1.0
        if len(tags) > 1:
            q = float(tags[1][2:])
        langs.add((q, loc_ins))
    return tuple(sorted(langs, reverse=True))
