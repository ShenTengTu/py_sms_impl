from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.routing import APIRoute
from sqlalchemy.orm import Session
from . import __version__, path_static
from .i18n import load_translations
from .middleware import setup_middleware
from .tmpl import template_response, template_context, TemplateResponseClass
from .routers import setup_router, tags_metadata
from .exception import setup_exception_handler, exception_redirect_reason
from .csrf import csrf_provider
from .sql.core import init_db, close_db, db_session
from .sql.orm import orm_metadata
from .crud.member import Member, MemberProfile
from .schema.member import MemberProfileRead


app = FastAPI(
    title="Simple Member System Implementation by FastAPI",
    description=(
        "Simple Member System Implementation "
        "(source: https://github.com/ShenTengTu/py_sms_impl) ."
    ),
    version=__version__,
    docs_url="/api-doc",
    redoc_url=None,
    openapi_tags=tags_metadata,
)
app.mount("/static", StaticFiles(directory=str(path_static)), name="static")


@app.on_event("startup")
async def startup_event():
    load_translations("en_US", "zh_TW", domain="py_sms_impl")
    init_db(orm_metadata())


@app.on_event("shutdown")
async def shutdown_event():
    close_db()


setup_exception_handler(app)
setup_middleware(app)
setup_router(app)


@app.get("/", tags=["Page"], response_class=TemplateResponseClass)
async def root(request: Request):
    return template_response("index.html", template_context(request))


@app.get("/sign-up", tags=["Page"], response_class=TemplateResponseClass)
async def sign_up(
    request: Request,
    csrf: tuple = Depends(csrf_provider()),
    rr: str = Depends(exception_redirect_reason),
):
    return template_response(
        "index.html", template_context(request, form_csrf=csrf, redirect_reason=rr)
    )


@app.get("/sign-in", tags=["Page"], response_class=TemplateResponseClass)
async def sign_in(
    request: Request,
    csrf: tuple = Depends(csrf_provider()),
    rr: str = Depends(exception_redirect_reason),
):
    return template_response(
        "index.html", template_context(request, form_csrf=csrf, redirect_reason=rr)
    )


@app.get("/@{user_name}", tags=["Page"], response_class=TemplateResponseClass)
def member_profile(
    request: Request,
    user_name: str,
    db: Session = Depends(db_session),
    rr: str = Depends(exception_redirect_reason),
):
    orm = Member.read(db, user_name=user_name)
    if orm is None:  # the member doesn't exist
        raise HTTPException(status_code=404)
    if orm.member_profile is None:  # create member profile if not exist
        MemberProfile.create(db, member_id=orm.member_id, display_name=orm.user_name)

    MemberProfileRead._default_avatar_path = "/static/img/default_avatar.svg"
    return template_response(
        "profile.html",
        template_context(
            request,
            redirect_reason=rr,
            user_name=orm.user_name,
            email_verified=orm.email_verified,
            member_profile=MemberProfileRead.from_orm(orm.member_profile),
        ),
    )


for route in app.routes:
    if isinstance(route, APIRoute):
        if not route.operation_id == route.name:
            route.operation_id = route.name
