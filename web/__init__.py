__version__ = "0.0.1"

from pathlib import Path
from enum import Enum, unique

path_package = Path(__file__).parent
path_templates = path_package / "templates"
path_static = path_package / "static"
path_locale = path_package / "../locale"


@unique
class E_RedirectReason(str, Enum):
    csrf_expired = "1"
    member_exists = "2"
    sign_up_completed = "3"
    sign_in_completed = "4"
    invalid_input = "5"
