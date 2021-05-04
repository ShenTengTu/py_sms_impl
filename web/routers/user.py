from fastapi import Request, Form, HTTPException
from pydantic import EmailStr
from ..schema.member import SignUpForm
from . import APIRouter, new_form_router


def setup(namesapce: str = "user", prefix: str = "/user"):
    router = APIRouter(prefix=prefix, tags=["User"]).namespace(namesapce)
    form_router = new_form_router()

    @form_router.post("/sign-up")
    async def sign_up(request: Request, form_data: SignUpForm):
        if not form_data.password == form_data.password_confirm:
            raise HTTPException(
                status_code=422, detail={"msg": "Password confirm mismatch."}
            )
        return request.session

    @form_router.post("/sign-in")
    async def sign_in(request: Request):
        return request.session

    router.include_router(form_router)
    return router
