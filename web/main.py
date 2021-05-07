from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.routing import APIRoute
from . import __version__, path_static
from .i18n import load_translations
from .middleware import setup_middleware
from .tmpl import template_response, template_context, TemplateResponseClass
from .routers import setup_router, tags_metadata
from .exception import setup_exception_handler
from .csrf import csrf_provider
from .sql.core import init_db
from .sql.orm import orm_metadata


app = FastAPI(
    title="Simple Member System Implementation by FastAPI",
    description=(
        "Simple Member System Implementation "
        "(source: https://github.com/ShenTengTu/py_sms_impl) ."
    ),
    version=__version__,
    docs_url="/api-doc",
    redoc_url=None,
    openapi_tags=tags_metadata,
)
app.mount("/static", StaticFiles(directory=str(path_static)), name="static")


@app.on_event("startup")
async def startup_event():
    load_translations("en_US", "zh_TW", domain="py_sms_impl")
    init_db(orm_metadata())


setup_exception_handler(app)
setup_middleware(app)
setup_router(app)


@app.get("/", tags=["Page"], response_class=TemplateResponseClass)
async def root(request: Request):
    return template_response("index.html", template_context(request))


@app.get("/sign-up", tags=["Page"], response_class=TemplateResponseClass)
async def sign_up(request: Request, csrf: tuple = Depends(csrf_provider())):
    return template_response("index.html", template_context(request, form_csrf=csrf))


@app.get("/sign-in", tags=["Page"], response_class=TemplateResponseClass)
async def sign_in(request: Request, csrf: tuple = Depends(csrf_provider())):
    return template_response("index.html", template_context(request, form_csrf=csrf))


for route in app.routes:
    if isinstance(route, APIRoute):
        if not route.operation_id == route.name:
            route.operation_id = route.name
