from fastapi import FastAPI
from . import __version__

app = FastAPI(
    title="Simple Member System Implementation by FastAPI",
    description="Simple Member System Implementation (source: https://github.com/ShenTengTu/py_sms_impl) .",
    version=__version__,
    docs_url="/api-doc",
    redoc_url=None,
)


@app.get("/")
async def root():
    return {"message": "Hello World"}
