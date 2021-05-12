import warnings
from sqlalchemy import exc as sql_exc
from sqlalchemy.orm import Session
from fastapi import HTTPException


class CRUD:
    orm = None

    @staticmethod
    def _commit(db: Session):
        """Flush pending changes and commit the current transaction.

        if `IntegrityError` occurs, rollback the current transaction in progress
        then raise `HTTPException`.
        """
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=sql_exc.SAWarning)
                db.commit()
        except sql_exc.IntegrityError as error:  # violates unique constraint
            db.rollback()
            name = error.orig.__class__.__name__
            if name == "UniqueViolation":
                raise RecordAlreadyExists(error.orig)
            elif name == "ForeignKeyViolation":
                raise RelatedRecordNotExist(error.orig)
            else:
                # IntegrityConstraintViolation
                # RestrictViolation
                # NotNullViolation
                # CheckViolation
                # ExclusionViolation
                print(name)
                raise HTTPException(500, detail=error.orig)

    @classmethod
    def create(cls, db: Session, *args, **kwargs):
        raise NotImplementedError("`CRUD.create` method is not implemented.")

    @classmethod
    def read(cls, db: Session, *args, **kwargs):
        raise NotImplementedError("`CRUD.read` method is not implemented.")

    @classmethod
    def update(cls, db: Session, *args, **kwargs):
        raise NotImplementedError("`CRUD.update` method is not implemented.")

    @classmethod
    def delete(cls, db: Session, *args, **kwargs):
        raise NotImplementedError("`CRUD.delete` method is not implemented.")


class RecordAlreadyExists(HTTPException):
    def __init__(self, message: str):
        super(HTTPException, self).__init__(500, detail=message)


class RelatedRecordNotExist(HTTPException):
    def __init__(self, message: str):
        super(HTTPException, self).__init__(500, detail=message)
