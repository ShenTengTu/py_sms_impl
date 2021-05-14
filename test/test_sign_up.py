import pytest
from httpx import AsyncClient
from web.csrf import DEFAULT_CSRF_NS
from web.schema.member import SignUpForm, MemberProfileRead
from web.crud.member import Member


class TestSignUp:
    url = "/api/user/form/sign-up"
    headers = {}
    form_data = {
        "user_id": "aB-c0_ef1",
        "email": "contact@testing.com",
        "password": "0z12@3456",
        "password_confirm": "0z12@3456",
    }

    async def mock_browse_page(self, async_client: AsyncClient, form_data: dict):
        # fetch csrf token
        resp = await async_client.get("/sign-up")

        for line in resp.iter_lines():
            l = line.strip()
            flag = 'name="form-csrf-token" value='
            pos = l.find(flag)
            if pos > 0:
                token = l[pos + len(flag) :].strip('">')
                form_data[DEFAULT_CSRF_NS] = token
                break
        # mock `referer` header
        self.headers.setdefault("referer", str(async_client.base_url.join("/sign-up")))

    @pytest.mark.asyncio
    async def test_setup(self, init_sql_db):
        init_sql_db()

    @pytest.mark.asyncio
    async def test_constraint(self, async_client: AsyncClient, testing_from_data: dict):
        form_data = testing_from_data.copy()

        async with async_client as ac:
            await self.mock_browse_page(ac, form_data)

            invalid_data = form_data.copy()

            # invalid user ID
            bads = ("0_ef", "xaB-", "-c0x", "xc0_", "_efx", "B-_e", "B--e", "B_-e", "B__e")
            for bad in bads:
                invalid_data["user_id"] = bad
                resp = await ac.post(self.url, data=invalid_data, headers=self.headers)
                assert resp.status_code == 422
            invalid_data["user_id"] = self.form_data["user_id"]

            # invalid e-ammil
            invalid_data["email"] = "name@host"
            resp = await ac.post(self.url, data=invalid_data, headers=self.headers)
            assert resp.status_code == 422
            invalid_data["email"] = self.form_data["email"]

            # invalid password
            bads = ("abc$defg", "012$3456")
            for bad in bads:
                invalid_data["password"] = bad
                invalid_data["password_confirm"] = bad
                resp = await ac.post(self.url, data=invalid_data, headers=self.headers)
                assert resp.status_code == 422
            invalid_data["password"] = self.form_data["password"]
            # invalid password confirm
            resp = await ac.post(self.url, data=invalid_data, headers=self.headers)
            assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_member_is_already_registered(
        self,
        async_client: AsyncClient,
        db_session_generator,
        demo_sign_up_form: SignUpForm,
    ):
        # Create demo member
        with db_session_generator() as db:
            orm = Member.read(db, user_name=demo_sign_up_form.user_id)
            if orm is None:
                orm = Member.create(db, form_data=demo_sign_up_form)

        form_data = demo_sign_up_form.dict()
        async with async_client as ac:
            await self.mock_browse_page(ac, form_data)
            resp = await ac.post(self.url, data=form_data, headers=self.headers)
            assert resp.status_code == 200
            assert resp.url == str(async_client.base_url.join("/sign-up"))
            lines = tuple(line.strip() for line in resp.iter_lines())
            assert '<div class="redirect-reason">' in lines
            assert "<p>The member is already registered.</p>" in lines

    @pytest.mark.asyncio
    async def test_registration_success(
        self,
        async_client: AsyncClient,
        testing_from_data: dict,
    ):
        form_data = testing_from_data.copy()
        async with async_client as ac:
            await self.mock_browse_page(ac, form_data)
            resp = await ac.post(self.url, data=form_data, headers=self.headers)
            assert resp.status_code == 200
            assert resp.url == str(async_client.base_url.join(f"/@{form_data['user_id']}"))
            lines = tuple(line.strip() for line in resp.iter_lines())
            assert '<span class="state-tag fail">Email isn&#39;t verified</span>' in lines
            assert f'src="{MemberProfileRead._default_avatar_path}"' in lines
            assert f'<span class="display-name">{form_data["user_id"]}</span>' in lines
            assert f'<span class="user-name">{form_data["user_id"]}</span>' in lines

    @pytest.mark.asyncio
    async def test_teardown(self, drop_sql_db, close_db):
        drop_sql_db()
        close_db()
