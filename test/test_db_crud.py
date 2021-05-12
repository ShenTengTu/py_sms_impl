from datetime import datetime
from typing import cast
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists
from web.settings import get_settings
from web.crypto import crypt_verify
from web.schema.member import SignUpForm
from web.crud import RecordAlreadyExists, RelatedRecordNotExist
from web.crud.member import Member, MemberProfile

form_data = {
    "user_id": "aB-c0_ef1",
    "email": "contact@testing.com",
    "password": "0z12@3456",
    "password_confirm": "0z12@3456",
}


def test_member_crud(init_sql_db, db_session_generator, drop_sql_db):
    init_sql_db()
    with db_session_generator() as db:
        db = cast(Session, db)

        # Create
        orm = Member.create(db, form_data=SignUpForm(**form_data))
        assert orm.member_id == 1
        assert orm.user_email == form_data["email"]
        assert orm.user_name == form_data["user_id"]
        assert crypt_verify(form_data["password"], orm.password_hash)
        assert type(orm.rigister_time) is datetime
        assert orm.email_verified == False

        # Duplicated creation
        with pytest.raises(RecordAlreadyExists):
            Member.create(db, form_data=SignUpForm(**form_data))

        # Read
        orm = Member.read(db, user_name=form_data["user_id"])
        assert orm.member_id == 1
        assert orm.user_email == form_data["email"]
        assert orm.user_name == form_data["user_id"]
        assert crypt_verify(form_data["password"], orm.password_hash)
        assert type(orm.rigister_time) is datetime
        assert orm.email_verified == False

        # Update
        new_pw = "0z12@3456X"
        assert 1 == Member.update(
            db, user_name=form_data["user_id"], password=new_pw, email_verified=True
        )
        orm = Member.read(db, user_name=form_data["user_id"])
        assert crypt_verify(new_pw, orm.password_hash)
        assert orm.email_verified == True

        # Delete
        assert 1 == Member.delete(db, user_name=form_data["user_id"])
        assert None == Member.read(db, user_name=form_data["user_id"])

    drop_sql_db()
    db.bind.dispose()  # Engine Disposal


def test_member_profile_crud(init_sql_db, db_session_generator, drop_sql_db):
    init_sql_db()
    with db_session_generator() as db:
        db = cast(Session, db)

        # The related record in `member` table does not exist
        with pytest.raises(RelatedRecordNotExist) as exc_info:
            MemberProfile.create(db, member_id=1, display_name="demo_user")

        # Create
        member_orm = Member.create(db, form_data=SignUpForm(**form_data))
        # relationship
        assert member_orm.member_profile is None
        orm = MemberProfile.create(
            db, member_id=member_orm.member_id, display_name=member_orm.user_name
        )
        assert orm.member_id == member_orm.member_id
        assert orm.display_name == member_orm.user_name
        assert orm.intro == None
        assert orm.avatar_path == None
        # relationship
        assert orm is member_orm.member_profile
        assert orm.member is member_orm

        # Duplicated creation
        with pytest.raises(RecordAlreadyExists):
            MemberProfile.create(
                db, member_id=member_orm.member_id, display_name=member_orm.user_name
            )

        # Read
        orm = MemberProfile.read(db, member_id=member_orm.member_id)
        assert orm.member_id == member_orm.member_id
        assert orm.display_name == member_orm.user_name
        assert orm.intro == None
        assert orm.avatar_path == None
        # relationship
        assert orm is member_orm.member_profile
        assert orm.member is member_orm

        # Update
        assert 1 == MemberProfile.update(
            db,
            member_id=member_orm.member_id,
            display_name="Demo User",
            intro="Demo User introduction",
            avatar_path="/static/avatar.jpg",
        )
        orm = MemberProfile.read(db, member_id=member_orm.member_id)
        assert orm.display_name == "Demo User"
        assert orm.intro == "Demo User introduction"
        assert orm.avatar_path == "/static/avatar.jpg"

        # Must be deleted by parent ORM `Member`
        with pytest.raises(NotImplementedError):
            MemberProfile.delete(db)

        # Delete
        Member.delete(db, user_name=member_orm.user_name)
        assert None == MemberProfile.read(db, member_id=member_orm.member_id)

    drop_sql_db()
    db.bind.dispose()  # Engine Disposal
