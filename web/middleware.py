from fastapi import FastAPI, Request
from .i18n import (
    get_translation,
    is_babel_translation,
    parse_accept_language,
)
from .tmpl import template_translation


def setup_middleware(app: FastAPI):
    """Setup all middlewares"""

    @app.middleware("http")
    async def observe_request_state(request: Request, call_next):
        print(request.state._state)
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
            request.headers["accept-language"]
        )
        response = await call_next(request)
        return response
