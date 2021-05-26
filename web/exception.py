from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import (
    http_exception_handler as _http_exception_handler,
    request_validation_exception_handler as _request_validation_exception_handler,
)
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from . import E_RedirectReason as E_RR
from .routers import get_endpoint_namespace
from .csrf import CSRFTokenExpired
from .crud import RecordAlreadyExists
from .tmpl import template_response, template_context


def setup_exception_handler(app: FastAPI):
    """Setup Exception handlers"""

    @app.exception_handler(CSRFTokenExpired)
    async def csrf_token_expired_handler(request: Request, exc: CSRFTokenExpired):
        ns = get_endpoint_namespace(request)
        if ns is None:
            return await http_exception_handler(request, exc)

        redirect_ns = None
        if ns == "api.user.form.sign_up":
            redirect_ns = "sign_up"
        elif ns == "api.user.form.sign_in":
            redirect_ns = "sign_in"

        if redirect_ns is None:
            return await http_exception_handler(request, exc)

        # 303 See Other
        # directing client to get requested resource to another URI with an GET request.
        request.session["redirect_reason"] = E_RR.csrf_expired.value
        return RedirectResponse(request.url_for(redirect_ns), status_code=303)

    @app.exception_handler(RecordAlreadyExists)
    async def record_already_exists_handler(request: Request, exc: RecordAlreadyExists):
        ns = get_endpoint_namespace(request)
        if ns is None:
            return await http_exception_handler(request, exc)

        redirect_ns = None
        redirect_reason = ""
        if ns == "api.user.form.sign_up":
            redirect_ns = "sign_up"
            redirect_reason = E_RR.member_exists.value

        if redirect_ns is None:
            return await http_exception_handler(request, exc)

        # 303 See Other
        # directing client to get requested resource to another URI with an GET request.
        request.session["redirect_reason"] = redirect_reason
        return RedirectResponse(request.url_for(redirect_ns), status_code=303)

    @app.exception_handler(SQLAlchemyError)
    async def sql_exception_handler(request: Request, exc: SQLAlchemyError):
        return await http_exception_handler(request, HTTPException(500, detail=exc))

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        ns = get_endpoint_namespace(request)
        if type(ns) is str and ns.startswith("api."):
            return await _http_exception_handler(request, exc)
        return template_response(
            "http_status_code.html",
            template_context(request, http_exc=exc),
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        ns = get_endpoint_namespace(request)
        if ns is None:
            return await _request_validation_exception_handler(request, exc)

        redirect_ns = None
        if ns == "api.user.form.sign_up":
            redirect_ns = "sign_up"
        elif ns == "api.user.form.sign_in":
            redirect_ns = "sign_in"

        if redirect_ns is None:
            return await _request_validation_exception_handler(request, exc)

        # 303 See Other
        # directing client to get requested resource to another URI with an GET request.
        request.session["redirect_reason"] = E_RR.invalid_input
        return RedirectResponse(request.url_for(redirect_ns), status_code=303)


def exception_redirect_reason(request: Request):
    """FastAPI dependency function to get the redirect reason code from the session."""
    rr: str = request.session.get("redirect_reason", None)
    if rr is not None:
        del request.session["redirect_reason"]
    return rr
