import pytest
from httpx import AsyncClient
from web.csrf import DEFAULT_CSRF_NS
from web.schema.member import SignUpForm, SignInForm, MemberProfileRead
from web.crud.member import Member


class TestSignUIn:
    url = "/api/user/form/sign-in"
    headers = {}

    @pytest.mark.asyncio
    async def test_constraint(
        self, async_client: AsyncClient, raw_sign_in_from_data: dict, async_mock_browse_form
    ):
        form_data = raw_sign_in_from_data.copy()

        async with async_client as ac:
            await async_mock_browse_form("/sign-in", ac, self.headers, form_data)

            invalid_data = form_data.copy()

            # invalid e-ammil
            invalid_data["email"] = "name@host"
            resp = await ac.post(self.url, data=invalid_data, headers=self.headers)
            assert resp.status_code == 200
            assert resp.url == str(async_client.base_url.join("/sign-in"))
            invalid_data["email"] = form_data["email"]

            # invalid password
            bads = ("abc$defg", "012$3456")
            for bad in bads:
                invalid_data["password"] = bad
                invalid_data["password_confirm"] = bad
                resp = await ac.post(self.url, data=invalid_data, headers=self.headers)
                assert resp.status_code == 200
                assert resp.url == str(async_client.base_url.join("/sign-in"))

    @pytest.mark.asyncio
    async def test_member_not_exist(
        self,
        async_client: AsyncClient,
        testing_sql_db_contextmanager,
        raw_sign_in_from_data: dict,
        async_mock_browse_form,
    ):
        with testing_sql_db_contextmanager():
            form_data = raw_sign_in_from_data.copy()
            async with async_client as ac:
                await async_mock_browse_form("/sign-in", ac, self.headers, form_data)
                resp = await ac.post(self.url, data=form_data, headers=self.headers)
                assert resp.status_code == 200
                assert resp.url == str(async_client.base_url.join("/sign-in"))
                lines = tuple(line.strip() for line in resp.iter_lines())
                assert '<div class="redirect-reason">' in lines
                assert "<p>Invalid inputs.</p>" in lines

    @pytest.mark.asyncio
    async def test_log_in_success(
        self,
        async_client: AsyncClient,
        testing_sql_db_contextmanager,
        db_session_generator,
        demo_sign_in_form: SignInForm,
        demo_sign_up_form: SignUpForm,
        async_mock_browse_form,
    ):
        with testing_sql_db_contextmanager():
            # Create demo member
            with db_session_generator() as db:
                orm = Member.read(db, user_name=demo_sign_in_form.email, is_email=True)
                if orm is None:
                    orm = Member.create(db, form_data=demo_sign_up_form)

            form_data = demo_sign_in_form.dict()
            async with async_client as ac:
                # password mismatch
                invalid_data = form_data.copy()
                p = invalid_data["password"]
                invalid_data["password"] = f"{p[0:2]}X{p[3:]}"
                await async_mock_browse_form("/sign-in", ac, self.headers, form_data)
                resp = await ac.post(self.url, data=invalid_data, headers=self.headers)

                # log in success
                await async_mock_browse_form("/sign-in", ac, self.headers, form_data)
                resp = await ac.post(self.url, data=form_data, headers=self.headers)
                assert resp.status_code == 200
                assert resp.url == str(async_client.base_url.join(f"/@{orm.user_name}"))
                lines = tuple(line.strip() for line in resp.iter_lines())
                assert (
                    '<span class="state-tag fail">Email isn&#39;t verified</span>' in lines
                )
                assert f'src="{MemberProfileRead._default_avatar_path}"' in lines
                assert f'<span class="display-name">{orm.user_name}</span>' in lines
                assert f'<span class="user-name">{orm.user_name}</span>' in lines
