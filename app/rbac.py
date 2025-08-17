from functools import wraps
from fastapi import HTTPException,status


class PermissionChecker:
    def __init__(self,roles:list[str] | str):
        self.roles = roles


    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            user = kwargs.get('current_user')
            if not user:
                # print(user)
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуется аутентификация")
            if 'admin' in user.role:
                return await func(*args, **kwargs)
            if not any(role in user.role for role in self.roles):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
            return await func(*args, **kwargs)
        return wrapper