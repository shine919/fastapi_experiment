from functools import wraps

from db import resources
from fastapi import HTTPException, status


class PermissionChecker:
    def __init__(self, roles: list[str] | str):
        self.roles = roles

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user_payload")
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Требуется аутентификация",
                )
            if "admin" in user.role:
                return await func(*args, **kwargs)
            if not any(role in user.role for role in self.roles):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
            return await func(*args, **kwargs)

        return wrapper


class AccessToDataChecker:
    def __init__(self, method):
        self.method = method

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user_payload")
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Требуется аутентификация access",
                )
            await self.get_access_to_data(user, kwargs.get("username"), self.method)
            return await func(*args, **kwargs)

        return wrapper

    @staticmethod
    async def get_access_to_data(user, needed_res: str, method: str):
        if method == "POST" and needed_res not in resources:
            return True
        if needed_res not in resources:
            raise HTTPException(status_code=404, detail="Такого ресурса не существует")
        if "admin" in user.role:
            return True
        if needed_res == user.username:
            return True
        if method == "GET":
            if resources[needed_res]["is_public"]:
                return True
            else:
                raise HTTPException(status_code=403, detail="This resource is not available")
        raise HTTPException(status_code=403, detail="Access denied")
