from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from . import __version__
from .i18n import load_translations, get_translation
from .tmpl import template_response, template_translation


app = FastAPI(
    title="Simple Member System Implementation by FastAPI",
    description="Simple Member System Implementation (source: https://github.com/ShenTengTu/py_sms_impl) .",
    version=__version__,
    docs_url="/api-doc",
    redoc_url=None,
)

load_translations("en_US", "zh_TW", domain="py_sms_impl")


@app.get("/")
async def root(request: Request):
    template_translation(get_translation("zh_TW"))
    return template_response("index.html", {"request": request})
