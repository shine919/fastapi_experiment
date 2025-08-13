from typing import Any

import pytest
from sqlalchemy import false, null

from db import get_session
from main import app


@pytest.mark.parametrize(
    "a, b, expected_status, expected_result",
    [
        (5, 10, 200, 15),
        (-8, -3, 200, -11),
        (0, 7, 200, 7),
        ("a", 10, 422, None),  # Ошибка валидации: строка вместо числа
        (3, None, 422, None)   # Отсутствует параметр b
    ]
)
async def test_calculate_sum_params(a, b, expected_status, expected_result, client):
    params = {"a": a}
    if b is not None:
        params["b"] = b

    response = await client.get("/sum/", params=params)
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json() == {"result": expected_result}

@pytest.mark.parametrize(
    "todo, expected_status, expected_result",
    [
        ({'title':'New todo','description':'New todo desc','user_id':1},200,{'message':'Todo created successfully'}),
        ({'title':1,'description':'New todo desc','user_id':1},422,None),
        ({'title':'cool todo','description':1,'user_id':1},422,None),
        ({'title':'cool todo','description':'cool_desc','user_id':99},404,{'detail':'User not found'}),
    ]
    )
async def test_create_todo(todo, expected_status, expected_result,client):
    response = await client.post('/todos/todo',json=todo)
    try:
        assert response.status_code == expected_status
        if response.status_code == 200:
            data = response.json()['result']
            assert data['title'] == todo['title']
            assert data['description'] == todo['description']
            assert data['user_id'] == todo['user_id']
            assert response.json()['message'] == expected_result['message']

    except Exception as e:
        pytest.fail(f'Тест не прошел:{e}')

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
