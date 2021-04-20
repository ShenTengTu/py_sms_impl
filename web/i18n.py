from pathlib import Path
from babel.support import Translations, NullTranslations


_translations_dict = {}


def load_translations(*locales: str, domain=None):
    """ Loads all translation of locales, fallback translation is first locale"""
    path_here = Path(__file__).parent
    _translations_dict.update(
        (loc, Translations.load(path_here / "../locale", loc, domain)) for loc in locales
    )
    _translations_dict["_fallback"] = _translations_dict[locales[0]]


def get_translation(locale: str):
    fb = _translations_dict.get("_fallback", NullTranslations())
    return _translations_dict.get(locale, fb)
