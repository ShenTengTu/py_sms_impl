from starlette.templating import _TemplateResponse
from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
from jinja2 import Markup
from . import path_templates, E_RedirectReason
from .schema import constraints
from .i18n import redirect_reasons as i18n_redirect_reasons
from .routers import get_endpoint_namespace


_templates = Jinja2Templates(directory=str(path_templates))
_templates.env.add_extension("jinja2.ext.i18n")

template_response = _templates.TemplateResponse
TemplateResponseClass = _TemplateResponse


def template_translation(translation):
    env = _templates.env
    env.uninstall_gettext_translations(None)
    env.install_gettext_translations(translation)


def template_context(
    request: Request,
    form_csrf: tuple = None,
    redirect_reason: int = None,
    http_exc: HTTPException = None,
    **entries,
):
    context = {}
    if type(form_csrf) is tuple:
        tmpl = '<input type="hidden" name="%s" value="%s">'
        context["csrf_field"] = Markup(tmpl % form_csrf)

    try:
        rr = E_RedirectReason(redirect_reason)
        context["redirect_reason"] = i18n_redirect_reasons.get(rr)
    except ValueError:
        context["redirect_reason"] = None

    context.update(
        request=request,
        endpoint_name=get_endpoint_namespace(request),
        constraints=constraints(),
        http_exception=http_exc,
    )

    for key, value in entries.items():
        context.setdefault(key, value)
    return context
