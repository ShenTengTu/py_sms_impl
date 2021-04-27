from fastapi import Request
from . import APIRouter


def setup(namesapce: str = "user", prefix: str = "/user"):
    router = APIRouter(prefix=prefix).namespace(namesapce)

    @router.post("/form-sign-up")
    async def form_sign_up(request: Request):
        return request.session

    @router.post("/form-sign-in")
    async def form_sign_in(request: Request):
        return request.session

    return router
