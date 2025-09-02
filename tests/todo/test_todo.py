import pytest


class TestTodoPost:
    @staticmethod
    @pytest.mark.parametrize(
        "todo, expected_status, expected_result",
        [
            (
                {"title": "New todo", "description": "New todo desc", "user_id": 1},
                200,
                {"message": "Todo created successfully"},
            ),
            ({"title": 1, "description": "New todo desc", "user_id": 1}, 422, None),
            ({"title": "cool todo", "description": 1, "user_id": 1}, 422, None),
            (
                {"title": "cool todo", "description": "cool_desc", "user_id": 99},
                404,
                {"detail": "User not found"},
            ),
        ],
    )
    async def test_create_todo(todo, expected_status, expected_result, client):
        response = await client.post("/todos/todo", json=todo)
        try:
            assert response.status_code == expected_status
            if response.status_code == 200:
                data = response.json()["result"]
                assert data["title"] == todo["title"]
                assert data["description"] == todo["description"]
                assert data["user_id"] == todo["user_id"]
                assert response.json()["message"] == expected_result["message"]

        except Exception as e:
            pytest.fail(f"Тест не прошел:{e}")


class TestTodoGets:
    @staticmethod
    @pytest.mark.parametrize(
        "expected_status, expected_result",
        [
            (200, None),
        ],
    )
    async def test_get_todos_positive(expected_status, expected_result, client):
        response = await client.get("/todos/todos")
        assert response.status_code == expected_status
        assert len(response.json()["todos"]) == 2

    @staticmethod
    @pytest.mark.parametrize(
        "expected_status, expected_result",
        [
            (404, {"detail": "Todos not found"}),
        ],
    )
    async def test_get_todos_negative(expected_status, expected_result, empty_db_client):
        # mock_get_todos_data = mocker.patch('todo.crud.TodoOrm.get_todos_with_params_orm')
        # mock_get_todos_data.side_effect = HTTPException(status_code=404, detail='Todos not found')
        response = await empty_db_client.get("/todos/todos")
        assert response.status_code == expected_status
        assert response.json()["detail"] == expected_result["detail"]

        # mock_get_todos_data.assert_called_once()


class TestTodoGetById:
    @staticmethod
    @pytest.mark.parametrize(
        "todo_id,expected_status, expected_result",
        [(1, 200, None), (99, 404, {"detail": "Todo not found"})],
    )
    async def test_get_todo_by_id_positive(todo_id, expected_status, expected_result, client):
        response = await client.get(f"/todos/todo/{todo_id}")
        assert response.status_code == expected_status
        if response.status_code == 200:
            assert response.json()["title"]
        else:
            assert response.json() == expected_result


class TestUpdateTodo:
    @staticmethod
    @pytest.mark.parametrize(
        "todo_id,todo,expected_status,expected_result",
        [
            (
                1,
                {
                    "title": "New title",
                    "description": "New description",
                    "completed": True,
                    "user_id": 1,
                },
                200,
                {"message": "Todo updated successfully!"},
            ),
            (
                1,
                {
                    "title": 1,
                    "description": "New description",
                    "completed": True,
                    "user_id": 1,
                },
                422,
                {
                    "error": "Validation error",
                    "details": [{"field": "title", "message": "Input should be a valid string"}],
                },
            ),
            (
                1,
                {
                    "title": "New Title",
                    "description": "New description",
                    "completed": True,
                    "user_id": 1000,
                },
                400,
                {"detail": "Invalid user"},
            ),
            (
                99,
                {
                    "title": "New Title",
                    "description": "New description",
                    "completed": True,
                    "user_id": 1000,
                },
                404,
                {"detail": "Todo not found"},
            ),
        ],
    )
    async def test_update_todo(todo_id, todo, expected_status, expected_result, client):
        response = await client.put(f"/todos/todo/{todo_id}", json=todo)
        assert response.status_code == expected_status
        assert response.json() == expected_result


class TestUpdateTodos:
    @staticmethod
    @pytest.mark.parametrize(
        "ids,completed,expected_status,expected_result",
        [
            (
                [
                    1,
                ],
                True,
                200,
                {"message": "Todos successfully updated"},
            ),
            ([1, 99], True, 404, {"detail": "Todos not found"}),
            ([100, 201], True, 404, {"detail": "Todos not found"}),
        ],
    )
    async def test_update_todos(ids, completed, expected_status, expected_result, client):
        response = await client.patch("todos/todos/", params={"ids": ids, "completed": completed})
        assert response.status_code == expected_status
        assert response.json() == expected_result


class TestDeleteTodo:
    @staticmethod
    @pytest.mark.parametrize(
        "todo_id,expected_status,expected_result",
        [
            (1, 200, {"message": "Todo deleted successfully"}),
            (99, 404, {"detail": "Todo not found"}),
        ],
    )
    async def test_delete_todo(todo_id, expected_status, expected_result, client):
        response = await client.delete(f"/todos/todo/{todo_id}")
        assert response.status_code == expected_status
        print(response.json())
