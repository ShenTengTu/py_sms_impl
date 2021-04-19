from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from . import __version__

app = FastAPI(
    title="Simple Member System Implementation by FastAPI",
    description="Simple Member System Implementation (source: https://github.com/ShenTengTu/py_sms_impl) .",
    version=__version__,
    docs_url="/api-doc",
    redoc_url=None,
)

templates = Jinja2Templates(directory="web/templates")
templates.env.add_extension("jinja2.ext.i18n")


@app.get("/")
async def root():
    return templates.TemplateResponse("index.html", {})
