import pytest
import requests

from main import app, fetch_data


class TestMock:
    async def test_simple(self, client):
        print("Тест выполняется!")
        resp = await client.get("users/user/2/")
        print(f"Статус: {resp.status_code}")
        print(f"Ответ: {resp.json()}")

    async def test_get_user(self, mocker, client):
        mock_usr_data = {"user": "admin", "id": 1}
        mock_f_data = requests.Timeout()
        mock_check_user = mocker.patch("user.crud.UserOrm.check_user_orm", return_value=mock_usr_data)
        mock_fetch_data = mocker.patch("main.get_rekt", return_value=mock_f_data)

        resp = await client.get("/users/user/1/")
        resp_2 = await fetch_data()
        assert isinstance(resp_2, Exception)
        mock_fetch_data.assert_called_once()
        mock_check_user.assert_called_once()

        assert resp.json() == mock_usr_data
        assert resp_2 == mock_f_data
