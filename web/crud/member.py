from datetime import datetime
from sqlalchemy import exc as sql_exc
from sqlalchemy.orm import Session
from ..sql.orm import MemberORM
from ..schema.member import SignUpForm
from ..crypto import crypt_hash
from . import CRUD, RecordAlreadyExists


class Member(CRUD):
    orm = MemberORM

    @classmethod
    def create(cls, db: Session, form_data: SignUpForm):
        orm_ins = cls.orm(
            user_email=form_data.email,
            user_name=form_data.user_id,
            password_hash=crypt_hash(form_data.password),
            rigister_time=datetime.now(),
        )
        try:
            db.add(orm_ins)
            db.commit()
        except sql_exc.IntegrityError as error:  # violates unique constraint
            db.rollback()
            raise RecordAlreadyExists(error.orig)
        db.refresh(orm_ins)
        return orm_ins

    @classmethod
    def read(cls, db: Session, user_name: str):
        return db.query(cls.orm).filter(cls.orm.user_name == user_name).first()

    @classmethod
    def update(
        cls,
        db: Session,
        user_name: str,
        *,
        password: str = None,
        email_verified: bool = None,
    ) -> int:

        d = {}

        if type(password) is str:
            d[cls.orm.password_hash] = crypt_hash(password)
        if type(email_verified) is bool:
            d[cls.orm.email_verified] = email_verified

        if len(d) == 0:
            return 0
        return db.query(cls.orm).filter(cls.orm.user_name == user_name).update(d)

    @classmethod
    def delete(cls, db: Session, user_name: str):
        return db.query(cls.orm).filter(cls.orm.user_name == user_name).delete()
