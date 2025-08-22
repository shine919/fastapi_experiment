import pytest


class TestUserAuth:
    @staticmethod
    @pytest.mark.parametrize(
        "user, expected_status, expected_result",
        [
            ({"username": "admin", "password": "admin"}, 200, {"access_token": str, "token_type": "bearer"}),
        ],
    )
    async def test_login(user, expected_status, expected_result, client):
        resp = await client.post("/users/login", data=user)
        assert resp.status_code == expected_status

        if resp.status_code == 200:
            assert resp.json()["token_type"] == expected_result["token_type"]

    @staticmethod
    @pytest.mark.parametrize(
        "user,user_resp,expected_status,expected_result",
        [
            (
                {"username": "admin", "password": "admin", "email": "example@mail.com"},
                "admin",
                200,
                {"Секретные данные Алисы"},
            ),
            (
                {"username": "alice", "password": "pass", "email": "example@mail.com"},
                "alice",
                200,
                {"Секретные данные Алисы"},
            ),
            ({"username": "bob", "password": "pass", "email": "example@mail.com"}, "alice", 403, None),
            (
                {"username": "markiz", "password": "pass", "email": "example@mail.com"},
                "bob",
                200,
                "Публичные заметки Боба",
            ),
        ],
    )
    async def test_auth(user, user_resp, expected_status, expected_result, client):
        register_resp = await client.post("users/register", json=user)
        print(register_resp, "REGISTER")
        login_resp = await client.post("users/login", data=user)
        token = login_resp.json()["access_token"]
        resp = await client.get(f"/users/protected_resource/{user_resp}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == expected_status
