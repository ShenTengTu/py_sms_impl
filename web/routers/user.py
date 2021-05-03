from fastapi import Request, Form, HTTPException
from pydantic import EmailStr
from ..settings import constraints
from . import APIRouter, new_form_router


def setup(namesapce: str = "user", prefix: str = "/user"):
    router = APIRouter(prefix=prefix, tags=["User"]).namespace(namesapce)
    form_router = new_form_router()

    c_user_id = constraints().user_id.dict()
    c_password = constraints().password.dict()

    @form_router.post("/sign-up")
    async def sign_up(
        request: Request,
        user_id: str = Form(..., **c_user_id),
        email: EmailStr = Form(...),
        password: str = Form(..., **c_password),
        password_confirm: str = Form(..., **c_password),
    ):
        if not password == password_confirm:
            raise HTTPException(
                status_code=422, detail={"msg": "Password confirm mismatch."}
            )
        return request.session

    @form_router.post("/sign-in")
    async def sign_in(request: Request):
        return request.session

    router.include_router(form_router)
    return router
