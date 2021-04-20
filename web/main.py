from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from . import __version__
from .i18n import load_translations

app = FastAPI(
    title="Simple Member System Implementation by FastAPI",
    description="Simple Member System Implementation (source: https://github.com/ShenTengTu/py_sms_impl) .",
    version=__version__,
    docs_url="/api-doc",
    redoc_url=None,
)

templates = Jinja2Templates(directory="web/templates")
templates.env.add_extension("jinja2.ext.i18n")
templates.env.install_gettext_translations(
    load_translations("en_US", "zh_TW", domain="py_sms_impl")
)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
