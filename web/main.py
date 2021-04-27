from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from . import __version__, path_static
from .i18n import load_translations
from .middleware import setup_middleware
from .tmpl import template_response, template_context


app = FastAPI(
    title="Simple Member System Implementation by FastAPI",
    description=(
        "Simple Member System Implementation "
        "(source: https://github.com/ShenTengTu/py_sms_impl) ."
    ),
    version=__version__,
    docs_url="/api-doc",
    redoc_url=None,
)
app.mount("/static", StaticFiles(directory=str(path_static)), name="static")


@app.on_event("startup")
async def startup_event():
    load_translations("en_US", "zh_TW", domain="py_sms_impl")


setup_middleware(app)


@app.get("/")
async def root(request: Request):
    return template_response("index.html", template_context(request))


@app.get("/sign-up")
async def sign_up(request: Request):
    return template_response("index.html", template_context(request, form_csrf=True))


@app.get("/sign-in")
async def sign_in(request: Request):
    return template_response("index.html", template_context(request, form_csrf=True))
