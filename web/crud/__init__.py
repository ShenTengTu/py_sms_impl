from abc import ABC
from fastapi import HTTPException


class CRUD(ABC):
    orm = None

    @classmethod
    def create(cls):
        pass

    @classmethod
    def read(cls):
        pass

    @classmethod
    def update(cls):
        pass

    @classmethod
    def delete(cls):
        pass

    @classmethod
    def exist(cls):
        pass


class RecordAlreadyExists(HTTPException):
    def __init__(self, message: str):
        super(HTTPException, self).__init__(500, detail=message)
