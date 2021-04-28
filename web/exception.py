from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import RedirectResponse
from .csrf import CSRFTokenExpired


def setup_exception_handler(app: FastAPI):
    """Setup Exception handlers"""

    @app.exception_handler(CSRFTokenExpired)
    async def csrf_token_expired_handler(request: Request, exc: CSRFTokenExpired):
        content_type = str(request.headers.get("content-type"))
        if content_type.startswith(
            ("multipart/form-data", "application/x-www-form-urlencoded")
        ):
            # 303 See Other
            # directing client to get requested resource to another URI with an GET request.
            return RedirectResponse(request.url_for("root"), status_code=303)
        else:
            return await http_exception_handler(request, exc)
