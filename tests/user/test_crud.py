import pytest
from security import crypt_context


class TestUserGet:
    @staticmethod
    @pytest.mark.parametrize(
        "user_id,expected_status,expected_result",
        [
            # ('testuser',None,False,200,{'id':1,'username':'testuser'}),
            (1, 200, {"id": 1, "username": "testuser"}),
            (99, 404, {"detail": "User not found"}),
            # ('testuser', None, True, 409, {'detail':"User with this name already exists"}),
            # (1, None, True, 422, {'detail': "User with this name already exists"}),
        ],
    )
    async def test_get_user_by_id(user_id, expected_status, expected_result, client):
        response = await client.get(f"/users/user/{user_id}/")
        print(response.json())
        assert response.status_code == expected_status
        if response.status_code == 200:
            assert response.json()["id"] == expected_result["id"]
            assert response.json()["username"] == expected_result["username"]


class TestUserGets:
    @staticmethod
    @pytest.mark.parametrize(
        "expected_status,expected_result",
        [
            (
                200,
                {
                    "users": [
                        {
                            "id": 1,
                            "username": "testuser",
                            "password": "$2b$12$HY5GOLej4VMKfutpObUGBOSx6BUwo8k6ngtimHkgbcl1oWNLYLBrW",
                            "email": "test@example.com",
                            "role": "user",
                        },
                        {
                            "id": 2,
                            "username": "admin",
                            "password": "$2b$12$6BvN8tSgn/pSBqqpXdGh/O9WR3cIIJ9kMJRHK5uG41P/AwG6AvNvi",
                            "email": "test@example.com",
                            "role": "admin",
                        },
                    ]
                },
            )
        ],
    )
    async def test_get_users(expected_status, expected_result, client):
        response = await client.get("/users/get_users/")
        print(response.json())

    @staticmethod
    @pytest.mark.parametrize("expected_status,expected_result", [(404, {"detail": "Users not found"})])
    async def test_get_users_empty_db(expected_status, expected_result, empty_db_client):
        response = await empty_db_client.get("/users/get_users/")
        assert response.status_code == expected_status
        assert response.json() == expected_result


class TestUserPut:
    @staticmethod
    @pytest.mark.parametrize(
        "user_id,user,expected_status,expected_result",
        [
            (
                1,
                {
                    "id": 1,
                    "username": "testuser",
                    "password": "123",
                    "email": "test@example.com",
                    "role": "user",
                },
                200,
                "The user with id 1 was updated successfully!",
            ),
            (
                4,
                {
                    "id": 1,
                    "username": "testuser",
                    "password": "123",
                    "email": "test@example.com",
                    "role": "user",
                },
                404,
                {"detail": "User not found"},
            ),
            (
                1,
                {
                    "id": 1,
                    "username": 1,
                    "password": "123",
                    "email": "test@example.com",
                    "role": "user",
                },
                422,
                {
                    "error": "Validation error",
                    "details": {
                        "field": "username",
                        "message": "Input should be a valid string",
                    },
                },
            ),
        ],
    )
    async def test_put_update_user(user_id, user, expected_status, expected_result, client):
        response = await client.put(f"/users/user/{user_id}", json=user)
        assert response.status_code == expected_status
        if response.status_code == 200:
            assert response.json()[0] == expected_result


class TestUserPatch:
    @staticmethod
    @pytest.mark.parametrize(
        "user_id,param,user,expected_status,expected_result",
        [
            (
                1,
                "username",
                {
                    "username": "testuserPATCH",
                },
                200,
                {"username": "testuserPATCH"},
            ),
            (
                1,
                "email",
                {
                    "email": "TEST@example.com",
                },
                200,
                {"email": "TEST@example.com"},
            ),
            (
                1,
                "password",
                {"password": "123"},
                200,
                {"password": crypt_context.hash("123")},
            ),
            (
                4,
                None,
                {
                    "id": 1,
                    "username": "testuser",
                    "password": "123",
                    "email": "test@example.com",
                    "role": "user",
                },
                404,
                {"detail": "User not found"},
            ),
            (
                1,
                None,
                {
                    "id": 1,
                    "username": 1,
                    "password": "123",
                    "email": "test@example.com",
                    "role": "user",
                },
                422,
                {
                    "error": "Validation error",
                    "details": {
                        "field": "username",
                        "message": "Input should be a valid string",
                    },
                },
            ),
        ],
    )
    async def test_patch_update_user(user_id, param, user, expected_status, expected_result, client):
        response = await client.patch(f"/users/user/{user_id}", json=user)
        assert response.status_code == expected_status
