from starlette.routing import get_name
from fastapi import FastAPI, APIRouter as _APIRouter, Depends, Request
from ..csrf import csrf_validator
from ..settings import get_settings


class APIRouter(_APIRouter):
    def add_api_route(self, path: str, endpoint, **kwargs):
        # Auto create an namespace of the route
        # `api_router_ns.sub_api_router_ns.endpoint_name`
        name = kwargs["name"]
        ns = get_name(endpoint) if name is None else name
        if hasattr(self, "_namespace"):
            ns = ".".join((self._namespace, ns))
        kwargs["name"] = ns
        kwargs["operation_id"] = ns
        setattr(endpoint, "_operation_id_", ns)
        super().add_api_route(path, endpoint, **kwargs)

    def namespace(self, ns: str):
        """Gives a namespace to the router"""
        if not hasattr(self, "_namespace"):
            self._namespace = ns
        return self


def get_endpoint_namespace(request: Request):
    """Get endpoint namespace."""
    ep = request.scope.get("endpoint", None)
    if ep is None:
        return None
    if hasattr(ep, "_operation_id_"):
        return str(ep._operation_id_)
    else:
        return get_name(ep)


def setup_router(app: FastAPI, namespace: str = "api", prefix: str = "/api"):

    from . import user

    router = APIRouter(prefix=prefix).namespace(namespace)
    router.include_router(user.setup())
    app.include_router(router)


def new_form_router():
    settings = get_settings()
    return APIRouter(
        prefix="/form",
        dependencies=[Depends(csrf_validator(time_limit=int(settings.max_age / 12)))],
        tags=["Form"],
    ).namespace("form")


tags_metadata = [
    {
        "name": "Page",
        "description": "HTML pages",
    },
    {
        "name": "User",
        "description": "Operations about user.",
    },
    {
        "name": "Form",
        "description": "Operations about form.",
    },
]
