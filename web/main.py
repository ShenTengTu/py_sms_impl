from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from . import __version__, path_static
from .i18n import (
    load_translations,
    get_translation,
    is_babel_translation,
    parse_accept_language,
)
from .tmpl import template_response, template_translation


app = FastAPI(
    title="Simple Member System Implementation by FastAPI",
    description="Simple Member System Implementation (source: https://github.com/ShenTengTu/py_sms_impl) .",
    version=__version__,
    docs_url="/api-doc",
    redoc_url=None,
)
app.mount("/static", StaticFiles(directory=str(path_static)), name="static")


@app.on_event("startup")
async def startup_event():
    load_translations("en_US", "zh_TW", domain="py_sms_impl")


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


@app.get("/")
async def root(request: Request):
    return template_response("index.html", {"request": request})
