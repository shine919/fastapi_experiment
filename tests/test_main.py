import pytest
import requests

from main import app, fetch_data




@pytest.mark.parametrize(
    "user, expected_status, expected_result",
    [
        ({'username':'admin','password':'admin'},200,{'access_token':str, 'token_type':'bearer'}),
    ]
)
async def test_login(user, expected_status, expected_result,client):
    resp = await client.post('/users/login',data=user)
    assert resp.status_code == expected_status


    if resp.status_code == 200:
        assert resp.json()['token_type'] == expected_result['token_type']

@pytest.mark.parametrize(
            'user,user_resp,expected_status,expected_result',[
                ({'username':'admin','password':'admin','email':'example@mail.com'},'admin',200,{"Секретные данные Алисы"}),
                ({'username':'alice','password':'pass','email':'example@mail.com'},'alice',200,{"Секретные данные Алисы"}),
                ({'username': 'bob', 'password': 'pass', 'email': 'example@mail.com'}, 'alice', 403,None),
                ({'username': 'markiz', 'password': 'pass', 'email': 'example@mail.com'}, 'bob', 200, "Публичные заметки Боба"),

    ]
        )
async def test_auth(user,user_resp, expected_status, expected_result,client):
    register_resp = await client.post('users/register',json=user)
    print(register_resp,'REGISTER')
    login_resp = await client.post('users/login',data=user)
    token  = login_resp.json()['access_token']
    resp = await client.get(f'/users/protected_resource/{user_resp}',headers={'Authorization':f'Bearer {token}'})
    assert resp.status_code == expected_status


class TestMock:

    async def test_simple(self,client):
        print("Тест выполняется!")
        resp = await client.get('users/user/2/')
        print(f"Статус: {resp.status_code}")
        print(f"Ответ: {resp.json()}")
    async def test_get_user(self, mocker, client):
        mock_usr_data = {'user':'admin','id':1}
        mock_f_data = requests.Timeout()
        mock_check_user = mocker.patch('user.crud.UserOrm.check_user_orm', return_value=mock_usr_data)
        mock_fetch_data = mocker.patch('main.get_rekt', return_value=mock_f_data)

        resp = await client.get('/users/user/1/')
        resp_2 = await fetch_data()
        assert isinstance(resp_2, Exception)
        mock_fetch_data.assert_called_once()
        mock_check_user.assert_called_once()

        assert resp.json() == mock_usr_data
        assert resp_2 == mock_f_data

































