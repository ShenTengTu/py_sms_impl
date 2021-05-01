from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi import FastAPI, Request
from .i18n import (
    get_translation,
    is_babel_translation,
    parse_accept_language,
)
from .tmpl import template_translation
from .settings import get_settings


def setup_middleware(app: FastAPI):
    """Setup all middlewares"""

    settings = get_settings()

    @app.middleware("http")
    async def observe_request_state(request: Request, call_next):
        # print(request.headers)
        response = await call_next(request)
        return response

    @app.middleware("http")
    async def update_translation(request: Request, call_next):
        trans = get_translation(None)  # null translation
        for _, locale in request.state.accept_language:
            trans = get_translation(locale)
            if is_babel_translation(trans):
                break
        template_translation(trans)
        response = await call_next(request)
        return response

    @app.middleware("http")
    async def parse_client_locale(request: Request, call_next):
        # get locale from HTTP header `Accept-Language`
        request.state.accept_language = parse_accept_language(
            request.headers.get("accept-language", "en-US")
        )
        response = await call_next(request)
        return response

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key.get_secret_value(),
        max_age=settings.max_age,
        same_site="strict",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_origin_regex=settings.origin_regex,
        allow_methods=settings.http_meothds,
    )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.hosts)
