from pathlib import Path
from fastapi.templating import Jinja2Templates


_templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
_templates.env.add_extension("jinja2.ext.i18n")

template_response = _templates.TemplateResponse


def template_translation(translation):
    env = _templates.env
    env.uninstall_gettext_translations(None)
    env.install_gettext_translations(translation)
