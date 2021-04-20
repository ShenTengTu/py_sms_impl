from pathlib import Path
from babel.support import Translations


def load_translations(*locales: str, domain=None):
    path_here = Path(__file__).parent
    return Translations.load(path_here / "../locale", locales, domain)
