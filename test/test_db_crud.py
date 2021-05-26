from datetime import datetime
import pytest
from web.crypto import crypt_verify
from web.schema.member import SignUpForm
from web.crud import RecordAlreadyExists, RelatedRecordNotExist
from web.crud.member import Member, MemberProfile


def test_member_crud(
    testing_sql_db_contextmanager,
    db_session_generator,
    testing_from_data: dict,
):
    with testing_sql_db_contextmanager():

        form_data = testing_from_data.copy()

        # Create
        with db_session_generator() as db:
            orm = Member.create(db, form_data=SignUpForm(**form_data))
            assert orm.member_id == 1
            assert orm.user_email == form_data["email"]
            assert orm.user_name == form_data["user_id"]
            assert crypt_verify(form_data["password"], orm.password_hash)
            assert type(orm.rigister_time) is datetime
            assert orm.email_verified == False

        # Duplicated creation]
        with db_session_generator() as db:
            with pytest.raises(RecordAlreadyExists):
                Member.create(db, form_data=SignUpForm(**form_data))

        # Read
        with db_session_generator() as db:
            orm = Member.read(db, user_name=form_data["user_id"])
            assert orm.member_id == 1
            assert orm.user_email == form_data["email"]
            assert orm.user_name == form_data["user_id"]
            assert crypt_verify(form_data["password"], orm.password_hash)
            assert type(orm.rigister_time) is datetime
            assert orm.email_verified == False

        # Update
        with db_session_generator() as db:
            new_pw = "0z12@3456X"
            assert 1 == Member.update(
                db, user_name=form_data["user_id"], password=new_pw, email_verified=True
            )
        with db_session_generator() as db:
            orm = Member.read(db, user_name=form_data["user_id"])
            assert crypt_verify(new_pw, orm.password_hash)
            assert orm.email_verified == True

        # Delete
        with db_session_generator() as db:
            assert 1 == Member.delete(db, user_name=form_data["user_id"])
            assert None == Member.read(db, user_name=form_data["user_id"])


def test_member_profile_crud(
    testing_sql_db_contextmanager,
    db_session_generator,
    testing_from_data: dict,
):
    with testing_sql_db_contextmanager():

        form_data = testing_from_data.copy()

        # The related record in `member` table does not exist
        with db_session_generator() as db:
            with pytest.raises(RelatedRecordNotExist) as exc_info:
                MemberProfile.create(db, member_id=1, display_name="demo_user")

        # Create
        with db_session_generator() as db:
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
        with db_session_generator() as db:
            with pytest.raises(RecordAlreadyExists):
                MemberProfile.create(
                    db, member_id=member_orm.member_id, display_name=member_orm.user_name
                )

        # Read
        with db_session_generator() as db:
            member_orm = Member.read(db, user_name=form_data["user_id"])
            orm = MemberProfile.read(db, member_id=member_orm.member_id)
            assert orm.member_id == member_orm.member_id
            assert orm.display_name == member_orm.user_name
            assert orm.intro == None
            assert orm.avatar_path == None
            # relationship
            assert orm is member_orm.member_profile
            assert orm.member is member_orm

            # create Pydantic model from ORM
            from web.schema.member import MemberProfileRead

            MemberProfileRead._default_avatar_path = "/static/avatar.jpg"
            m = MemberProfileRead.from_orm(member_orm.member_profile)
            assert m.display_name == orm.display_name
            assert m.intro == ""
            assert m.avatar_path == "/static/avatar.jpg"

        # Update
        with db_session_generator() as db:
            assert 1 == MemberProfile.update(
                db,
                member_id=member_orm.member_id,
                display_name="Demo User",
                intro="Demo User introduction",
                avatar_path="/static/avatar.jpg",
            )
        with db_session_generator() as db:
            orm = MemberProfile.read(db, member_id=member_orm.member_id)
            assert orm.display_name == "Demo User"
            assert orm.intro == "Demo User introduction"
            assert orm.avatar_path == "/static/avatar.jpg"

        # Must be deleted by parent ORM `Member`
        with db_session_generator() as db:
            with pytest.raises(NotImplementedError):
                MemberProfile.delete(db)

        # Delete
        with db_session_generator() as db:
            Member.delete(db, user_name=member_orm.user_name)
            assert None == MemberProfile.read(db, member_id=member_orm.member_id)
