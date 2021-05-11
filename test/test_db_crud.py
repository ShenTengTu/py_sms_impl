from datetime import datetime
from typing import cast
import pytest
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists
from web.settings import get_settings
from web.crypto import crypt_verify
from web.schema.member import SignUpForm
from web.crud import RecordAlreadyExists
from web.crud.member import Member


class Test_DB_CRUD:
    def test_member_crud(self, init_sql_db, db_session_generator, drop_sql_db):
        form_data = {
            "user_id": "aB-c0_ef1",
            "email": "contact@testing.com",
            "password": "0z12@3456",
            "password_confirm": "0z12@3456",
        }

        init_sql_db()
        with db_session_generator() as db:
            db = cast(Session, db)

            orm = Member.create(db, SignUpForm(**form_data))
            assert orm.member_id == 1
            assert orm.user_email == form_data["email"]
            assert orm.user_name == form_data["user_id"]
            assert crypt_verify(form_data["password"], orm.password_hash)
            assert type(orm.rigister_time) is datetime
            assert orm.email_verified == False

            # Duplicated creation
            with pytest.raises(RecordAlreadyExists):
                Member.create(db, SignUpForm(**form_data))

            # Read
            orm = Member.read(db, form_data["user_id"])
            assert orm.member_id == 1
            assert orm.user_email == form_data["email"]
            assert orm.user_name == form_data["user_id"]
            assert crypt_verify(form_data["password"], orm.password_hash)
            assert type(orm.rigister_time) is datetime
            assert orm.email_verified == False

            # Update
            new_pw = "0z12@3456X"
            assert 1 == Member.update(
                db, form_data["user_id"], password=new_pw, email_verified=True
            )
            assert 1 == Member.update(
                db, form_data["user_id"], password=new_pw, email_verified=True
            )
            orm = Member.read(db, form_data["user_id"])
            assert crypt_verify(new_pw, orm.password_hash)
            assert orm.email_verified == True

            # Delete
            assert 1 == Member.delete(db, form_data["user_id"])
            assert None == Member.read(db, form_data["user_id"])

        drop_sql_db()
        db.bind.dispose()  # Engine Disposal
