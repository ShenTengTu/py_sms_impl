from functools import lru_cache
from pydantic import BaseSettings, BaseModel


class StringConstraint(BaseModel):
    min_length: int = None
    max_length: int = None
    regex: str = None


class _Constraints(BaseSettings):
    user_id: StringConstraint = StringConstraint(
        min_length=4, max_length=32, regex=r"^[a-zA-Z]([_-]?[a-zA-Z0-9]+)+$"
    )
    password: StringConstraint = StringConstraint(
        min_length=8, regex=r"^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9@#$%^&+=*._-]){8,}$"
    )


@lru_cache()
def constraints():
    return _Constraints()
