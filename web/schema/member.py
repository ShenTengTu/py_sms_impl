from typing import Optional
from fastapi import Form, HTTPException
from pydantic import BaseModel, EmailStr, root_validator, Field
from . import constraints

_c_user_id = constraints().user_id.dict()
_c_password = constraints().password.dict()


class SignUpForm(BaseModel):
    user_id: str
    email: EmailStr
    password: str
    password_confirm: str

    @classmethod
    def parse(
        cls,
        user_id: str = Form(..., **_c_user_id),
        email: EmailStr = Form(...),
        password: str = Form(..., **_c_password),
        password_confirm: str = Form(..., **_c_password),
    ):
        return cls(
            user_id=user_id,
            email=email,
            password=password,
            password_confirm=password_confirm,
        )

    @root_validator
    def check_password_confirm(cls, values):
        if values.get("password") != values.get("password_confirm"):
            raise HTTPException(
                status_code=422, detail={"msg": "Password confirm mismatch."}
            )
        return values


class SignInForm(BaseModel):
    email: EmailStr
    password: str

    @classmethod
    def parse(cls, email: EmailStr = Form(...), password: str = Form(..., **_c_password)):
        return cls(email=email, password=password)


class MemberProfileRead(BaseModel):
    _default_avatar_path = ""
    display_name: Optional[str] = Field(max_length=64)
    intro: Optional[str] = Field(max_length=256)
    avatar_path: Optional[str]

    class Config:
        orm_mode = True

    @root_validator
    def default_values(cls, values):
        if values.get("display_name") is None:
            values["display_name"] = ""
        if values.get("intro") is None:
            values["intro"] = ""
        if values.get("avatar_path") is None:
            values["avatar_path"] = cls._default_avatar_path
        return values
