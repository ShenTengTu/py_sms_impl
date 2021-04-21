from pathlib import Path
from fastapi.templating import Jinja2Templates
from . import path_templates


_templates = Jinja2Templates(directory=str(path_templates))
_templates.env.add_extension("jinja2.ext.i18n")

template_response = _templates.TemplateResponse


def template_translation(translation):
    env = _templates.env
    env.uninstall_gettext_translations(None)
    env.install_gettext_translations(translation)
