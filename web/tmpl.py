from starlette.routing import get_name
from starlette.templating import _TemplateResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import Markup
from . import path_templates
from .settings import constraints


_templates = Jinja2Templates(directory=str(path_templates))
_templates.env.add_extension("jinja2.ext.i18n")

template_response = _templates.TemplateResponse
TemplateResponseClass = _TemplateResponse


def template_translation(translation):
    env = _templates.env
    env.uninstall_gettext_translations(None)
    env.install_gettext_translations(translation)


def template_context(request: Request, form_csrf: tuple = None, **entries):
    context = {}
    if type(form_csrf) is tuple:
        tmpl = '<input type="hidden" name="%s" value="%s">'
        context["csrf_field"] = Markup(tmpl % form_csrf)

    context.update(
        request=request,
        endpoint_name=get_name(request.scope["endpoint"]),
        constraints=constraints(),
    )

    for key, value in entries:
        context.setdefault(key, value)
    return context
