import pytest
from httpx import AsyncClient
from web.schema.member import SignUpForm, MemberProfileRead
from web.crud.member import Member, MemberProfile


class TestMemeberProfile:
    @pytest.mark.asyncio
    async def test_setup(self, init_sql_db):
        init_sql_db()

    @pytest.mark.asyncio
    async def test_not_exist(self, async_client: AsyncClient):
        async with async_client as ac:
            resp = await ac.get("/@not-exist")
            assert resp.status_code == 404
            lines = tuple(line.strip() for line in resp.iter_lines())
            assert '<p class="status-code">404</p>' in lines
            assert '<p class="detail">Not Found</p>' in lines

    @pytest.mark.asyncio
    async def test_memeber_exists(
        self,
        async_client: AsyncClient,
        db_session_generator,
        demo_sign_up_form: SignUpForm,
        demo_member_profile: dict,
    ):
        # Create demo member
        with db_session_generator() as db:
            orm = Member.read(db, user_name=demo_sign_up_form.user_id)
            if orm is None:
                orm = Member.create(db, form_data=demo_sign_up_form)
                MemberProfile.create(
                    db, member_id=orm.member_id, display_name=orm.user_name
                )
            Member.update(db, user_name=orm.user_name, email_verified=True)
            MemberProfile.update(db, member_id=orm.member_id, **demo_member_profile)

            async with async_client as ac:
                resp = await ac.get(f"/@{demo_sign_up_form.user_id}")
                assert resp.status_code == 200
                lines = tuple(line.strip() for line in resp.iter_lines())
                assert '<span class="state-tag success">Email verified</span>' in lines
                assert f'src="{MemberProfileRead._default_avatar_path}"' in lines
                assert (
                    f'<span class="display-name">{demo_member_profile["display_name"]}</span>'
                    in lines
                )
                assert (
                    f'<span class="user-name">{demo_sign_up_form.user_id}</span>' in lines
                )
                assert f"<div>{demo_member_profile['intro']}</div>" in lines

    @pytest.mark.asyncio
    async def test_teardown(self, drop_sql_db, close_db):
        drop_sql_db()
        close_db()
