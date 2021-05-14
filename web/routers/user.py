from fastapi import Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .. import E_RedirectReason
from ..schema.member import SignUpForm
from ..sql.core import db_session
from ..crud.member import Member
from . import APIRouter, new_form_router


def setup(namesapce: str = "user", prefix: str = "/user"):
    router = APIRouter(prefix=prefix, tags=["User"]).namespace(namesapce)
    form_router = new_form_router()

    @form_router.post("/sign-up")
    def sign_up(
        request: Request,
        form_data: SignUpForm = Depends(SignUpForm.parse),
        db: Session = Depends(db_session),
    ):
        # This operation maybe raise `RecordAlreahodyExists` error,
        # See how `exception.py` handles the error.
        orm = Member.create(db, form_data=form_data)

        request.session["redirect_reason"] = E_RedirectReason.sin_up_completed.value
        return RedirectResponse(
            request.url_for("member_profile", user_name=orm.user_name), status_code=303
        )

    @form_router.post("/sign-in")
    async def sign_in(request: Request):
        return request.session

    router.include_router(form_router)
    return router
