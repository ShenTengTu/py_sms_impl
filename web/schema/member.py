from fastapi import Form, HTTPException
from pydantic import BaseModel, EmailStr, root_validator
from . import constraints

_c_user_id = constraints().user_id.dict()
_c_password = constraints().password.dict()


class SignUpForm(BaseModel):
    user_id: str = Form(..., **_c_user_id)
    email: EmailStr = Form(...)
    password: str = Form(..., **_c_password)
    password_confirm: str = Form(..., **_c_password)

    @root_validator
    def check_password_confirm(cls, values):
        if values.get("password") != values.get("password_confirm"):
            raise HTTPException(
                status_code=422, detail={"msg": "Password confirm mismatch."}
            )
        return values
