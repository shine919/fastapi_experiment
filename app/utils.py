from datetime import datetime
from functools import wraps

from core.config import settings
from db import USERS_DATA, get_session, resources
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi_limiter.depends import RateLimiter
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from security import get_user_from_token, oauth2_scheme
from sqlalchemy.ext.asyncio import AsyncSession
from user.crud import UserOrm
from user.schema import UserCheck, UserFromDB

serializer = URLSafeTimedSerializer(
    secret_key=settings.secret_key,
    salt=settings.salt,
)


async def check_token_time(user_name, time, response: Response):
    now = datetime.now().timestamp()
    if 180 < float(now) - float(time) < 300:
        token = await create_token(user_name)
        response.set_cookie(key="session_token", value=token, max_age=300, httponly=True)
        for user in USERS_DATA:
            if user["username"] == user_name:
                user["session_token"] = token
        return True
    elif 180 > float(now) - float(time):
        return True
    else:
        response.delete_cookie(key="session_token")
        return False


async def create_token(user_id):
    timestamp = int(datetime.now().timestamp())
    data = f"{user_id}.{timestamp}"
    result = serializer.dumps(data)
    return f"{data}.{result}"


async def verify_token(token, response: Response, max_age=1800):
    token_list = token.split(".")
    signature = ".".join(token_list[2:])
    time = token_list[1]
    user_id = token_list[0]
    try:
        verify_signature = serializer.loads(signature, max_age=max_age)
        decoded_data = verify_signature.split(".")
        if decoded_data[0] == user_id and decoded_data[1] == time:
            pass
        else:
            raise BadSignature("msg")
        if not await check_token_time(user_id, time, response):
            raise SignatureExpired("msg")
        return {"message": "success"}
    except BadSignature:
        return {"message": "Invalid session"}
    except SignatureExpired:
        return {"message": "Signature expired"}


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    username = await get_user_from_token(token)
    usr = await UserOrm.check_user_orm(username=username, session=session)
    return usr


limits_rate_dict = {
    "admin": 1000,
    "user": 20,
    "guest": 5,
}


async def get_limit_time_by_role(request: Request, response: Response, user: UserFromDB = Depends(get_current_user)):
    for k, v in limits_rate_dict.items():
        if k in user.roles:
            limiter = RateLimiter(times=v, minutes=1)
            return await limiter(request=request, response=response)
    limiter = RateLimiter(times=5, minutes=1)
    return await limiter(request=request, response=response)


async def get_request_method(request: Request):
    return request.method


class AccessToDataChecker:
    def __init__(self, method):
        self.method = method

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Требуется аутентификация access",
                )
            await get_access_to_data(user, kwargs.get("username"), self.method)
            return await func(*args, **kwargs)

        return wrapper


async def get_access_to_data(user: UserCheck, needed_res: str, method: str):
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
