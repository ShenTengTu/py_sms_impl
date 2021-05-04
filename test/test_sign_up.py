import pytest
from httpx import AsyncClient
from web.csrf import DEFAULT_CSRF_NS


class TestSignUp:
    url = "/api/user/form/sign-up"
    headers = {}
    form_data = {
        "user_id": "aB-c0_ef1",
        "email": "contact@testing.com",
        "password": "0z12@3456",
        "password_confirm": "0z12@3456",
    }

    async def mock_browse_page(self, async_client: AsyncClient):
        # fetch csrf token
        resp = await async_client.get("/sign-up")

        for line in resp.iter_lines():
            l = line.strip()
            flag = 'name="form-csrf-token" value='
            pos = l.find(flag)
            if pos > 0:
                token = l[pos + len(flag) :].strip('">')
                self.form_data[DEFAULT_CSRF_NS] = token
                break
        # mock `referer` header
        self.headers.setdefault("referer", str(async_client.base_url.join("/sign-up")))

    @pytest.mark.asyncio
    async def test_constraint(self, async_client: AsyncClient):
        async with async_client as ac:
            await self.mock_browse_page(ac)

            invalid_data = self.form_data.copy()

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
