from datetime import datetime
from sqlalchemy.orm import Session
from ..sql.orm import MemberORM, MemberProfileORM
from ..schema.member import SignUpForm
from ..crypto import crypt_hash
from . import CRUD


class Member(CRUD):
    orm = MemberORM

    @classmethod
    def create(cls, db: Session, *, form_data: SignUpForm):
        orm_ins = cls.orm(
            user_email=form_data.email,
            user_name=form_data.user_id,
            password_hash=crypt_hash(form_data.password),
            rigister_time=datetime.now(),
        )
        db.add(orm_ins)
        cls._commit(db)
        db.refresh(orm_ins)
        return orm_ins

    @classmethod
    def read(cls, db: Session, *, user_name: str):
        return db.query(cls.orm).filter(cls.orm.user_name == user_name).first()

    @classmethod
    def update(
        cls,
        db: Session,
        *,
        user_name: str,
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

        c = db.query(cls.orm).filter(cls.orm.user_name == user_name).update(d)
        cls._commit(db)
        return c

    @classmethod
    def delete(cls, db: Session, *, user_name: str):
        c = db.query(cls.orm).filter(cls.orm.user_name == user_name).delete()
        cls._commit(db)
        return c


class MemberProfile(CRUD):
    orm = MemberProfileORM

    @classmethod
    def create(cls, db: Session, *, member_id: int, display_name: str):
        orm_ins = cls.orm(member_id=member_id, display_name=display_name)
        db.add(orm_ins)
        cls._commit(db)
        db.refresh(orm_ins)
        return orm_ins

    @classmethod
    def read(cls, db: Session, *, member_id: int):
        return db.query(cls.orm).filter(cls.orm.member_id == member_id).first()

    @classmethod
    def update(
        cls,
        db: Session,
        *,
        member_id: int,
        display_name: str = None,
        intro: str = None,
        avatar_path: str = None,
    ):
        d = {}

        if type(display_name) is str:
            d[cls.orm.display_name] = display_name
        if type(intro) is str:
            d[cls.orm.intro] = intro
        if type(avatar_path) is str:
            d[cls.orm.avatar_path] = avatar_path

        if len(d) == 0:
            return 0
        c = db.query(cls.orm).filter(cls.orm.member_id == member_id).update(d)
        cls._commit(db)
        return c
