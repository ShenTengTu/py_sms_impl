from starlette.routing import get_name
from starlette.templating import _TemplateResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import Markup
from . import path_templates
from .csrf import setup_crsf
from .settings import get_settings


_templates = Jinja2Templates(directory=str(path_templates))
_templates.env.add_extension("jinja2.ext.i18n")

template_response = _templates.TemplateResponse
TemplateResponseClass = _TemplateResponse


def template_translation(translation):
    env = _templates.env
    env.uninstall_gettext_translations(None)
    env.install_gettext_translations(translation)


def template_context(request: Request, form_csrf=False, **entries):
    settings = get_settings()
    context = {}
    if form_csrf:
        tmpl = '<input type="hidden" name="%s" value="%s">'
        ns = form_csrf if type(form_csrf) is str else "form-csrf-token"
        token = setup_crsf(request, settings.secret_key.get_secret_value(), ns)
        context["csrf_field"] = Markup(tmpl % (ns, token))

    context.update(request=request, endpoint_name=get_name(request.scope["endpoint"]))

    for key, value in entries:
        context.setdefault(key, value)
    return context
