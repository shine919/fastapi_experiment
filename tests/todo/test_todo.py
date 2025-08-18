"""TEST TODO ADD"""
import pytest


class TestTodoPost:
    @staticmethod
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



class TestTodoGet:
    @staticmethod
    @pytest.mark.parametrize(
        "expected_status, expected_result",
        [
            (200,None),
        ]
    )
    async def test_get_todos_positive(expected_status,expected_result,client):
        response = await client.get('/todos/todos')
        print(response.json(),response.status_code)
