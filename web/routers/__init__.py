from starlette.routing import get_name
from fastapi import FastAPI, APIRouter as _APIRouter


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
        super().add_api_route(path, endpoint, **kwargs)

    def namespace(self, ns: str):
        """Gives a namespace to the router"""
        if not hasattr(self, "_namespace"):
            self._namespace = ns
        return self


def setup_router(app: FastAPI, namespace: str = "api", prefix: str = "/api"):

    from . import user

    router = APIRouter(prefix=prefix).namespace(namespace)
    router.include_router(user.setup())
    app.include_router(router)
