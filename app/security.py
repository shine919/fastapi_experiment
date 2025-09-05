import datetime
import json
from typing import Dict

import bcrypt
import jwt
import redis.asyncio as redis
from core.config import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

bcrypt.__about__ = bcrypt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 2
REFRESH_TOKEN_EXPIRES_MINUTES = 30

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ROLES_DICT = {1: "admin", 2: "user", 3: "guest"}

redis_pool = redis.Redis(host="127.0.0.1", db=1, decode_responses=True)


async def check_delete_token_in_redis(token, client_ip, user_agent):
    r = await redis_pool
    try:
        payload_json = await r.get("token")
        payload = json.loads(payload_json)
        if (payload.get("ip_address", None) != client_ip) or payload.get("user_agent") != user_agent:
            await r.delete(token)
            await r.delete(f"user:{payload['id']}")
            raise HTTPException(status_code=401, detail="Security violation detected. Token revoked.")
        await r.srem(f"user:{payload['id']}", token)
        await r.delete(token)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Token not found {e}")


async def verify_token(token):
    try:
        payload = jwt.decode(token, key=settings.secret_key, algorithms=ALGORITHM)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token invalid: {str(e)}")


async def put_token_to_redis(data: dict, token: str):
    uid = data["id"]
    payload = {
        "id": uid,
        "exp": data["exp"],
        "iat": data["iat"],
        "role": data["role"],
        "user_agent": data["user_agent"],
        "ip_address": data["ip_address"],
    }
    r = await redis_pool
    await r.sadd(f"user:{uid}", token)
    await r.expire(f"user:{uid}", time=60 * REFRESH_TOKEN_EXPIRES_MINUTES)
    await r.setex(name=f"{uid}:{token}", value=json.dumps(payload), time=60 * REFRESH_TOKEN_EXPIRES_MINUTES)


async def create_tokens(data: Dict):
    access_data = data.copy()
    refresh_data = data.copy()
    expire_access = datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    expire_refresh = datetime.datetime.now() + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRES_MINUTES)
    iat = datetime.datetime.now(datetime.timezone.utc)
    access_data.update({"iat": iat, "exp": expire_access, "type": "access"})
    refresh_data.update({"iat": iat, "exp": expire_refresh, "type": "refresh"})
    access_token = jwt.encode(access_data, settings.secret_key, algorithm=ALGORITHM)
    refresh_token = jwt.encode(refresh_data, settings.secret_key, algorithm=ALGORITHM)
    await put_token_to_redis(refresh_data, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token}


async def take_new_refresh(token, client_ip, user_agent):
    payload = await verify_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    await check_delete_token_in_redis(token, client_ip, user_agent)
    return await create_tokens(payload)


async def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
