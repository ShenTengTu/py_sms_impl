from starlette.routing import get_name
from fastapi import Request
from fastapi.templating import Jinja2Templates
from . import path_templates


_templates = Jinja2Templates(directory=str(path_templates))
_templates.env.add_extension("jinja2.ext.i18n")

template_response = _templates.TemplateResponse


def template_translation(translation):
    env = _templates.env
    env.uninstall_gettext_translations(None)
    env.install_gettext_translations(translation)


def template_context(request: Request, **entries):
    context = {"request": request, "endpoint_name": get_name(request.scope["endpoint"])}

    for key, value in entries:
        context.setdefault(key, value)
    return context
