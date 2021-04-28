__version__ = "0.0.1"

from pathlib import Path

path_package = Path(__file__).parent
path_templates = path_package / "templates"
path_static = path_package / "static"
path_locale = path_package / "../locale"
