from fastapi import Form
from pydantic import BaseModel, EmailStr
from . import constraints

_c_user_id = constraints().user_id.dict()
_c_password = constraints().password.dict()


class SignUpForm(BaseModel):
    user_id: str = Form(..., **_c_user_id)
    email: EmailStr = Form(...)
    password: str = Form(..., **_c_password)
    password_confirm: str = Form(..., **_c_password)
