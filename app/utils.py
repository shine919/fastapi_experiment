import jwt
from core.config import settings
from fastapi import Depends, HTTPException, Request, Response
from fastapi_limiter.depends import RateLimiter
from itsdangerous import URLSafeTimedSerializer
from security import ALGORITHM, PayloadFromJWT, oauth2_scheme

serializer = URLSafeTimedSerializer(
    secret_key=settings.secret_key,
    salt=settings.salt,
)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = await get_payload_from_token(token)
    return payload


async def get_payload_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return PayloadFromJWT(
            id=payload["id"],
            username=payload["sub"],
            role=payload["role"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


limits_rate_dict = {
    "admin": 1000,
    "user": 20,
    "guest": 5,
}


async def get_limit_time_by_role(
    request: Request, response: Response, user: PayloadFromJWT = Depends(get_current_user)
):
    for k, v in limits_rate_dict.items():
        if k in user.role:
            limiter = RateLimiter(times=v, minutes=1)
            return await limiter(request=request, response=response)
    limiter = RateLimiter(times=5, minutes=1)
    return await limiter(request=request, response=response)


async def get_request_method(request: Request):
    return request.method
