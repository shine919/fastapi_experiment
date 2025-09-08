import datetime
import json
from typing import Dict

import bcrypt
import jwt
import redis.asyncio as redis
from core.config import settings
from core.logger import get_logger
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel

bcrypt.__about__ = bcrypt
logger = get_logger()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 2
REFRESH_TOKEN_EXPIRES_MINUTES = 30

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ROLES_DICT = {1: "admin", 2: "user", 3: "guest"}


class PayloadFromJWT(BaseModel):
    id: int
    username: str
    role: str


class TokenManager:
    def __init__(self):
        self.redis = redis.Redis(host="127.0.0.1", db=1, decode_responses=True)

    async def check_delete_token_in_redis(self, token, client_ip, user_agent):
        try:
            payload_json = await self.redis.get("token")
            payload = json.loads(payload_json)
            uid = payload["id"]
            if (payload.get("ip_address", None) != client_ip) or payload.get("user_agent") != user_agent:
                await self.redis.delete(token)
                await self.redis.delete(f"user:{uid}")
                raise HTTPException(status_code=401, detail="Security violation detected. Token revoked.")
            await self.redis.srem(f"user:{uid}", token)
            await self.redis.delete(f"{uid}:{token}")
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Token not found {e}")

    async def put_token_to_redis(self, data: dict, token: str):
        uid = data["id"]
        payload = {
            "id": uid,
            "sub": data["sub"],
            "exp": data["exp"],
            "iat": data["iat"],
            "role": data["role"],
            "user_agent": data["user_agent"],
            "ip_address": data["ip_address"],
        }
        logger.info(payload)

        await self.redis.sadd(f"user:{uid}", token)
        await self.redis.expire(f"user:{uid}", time=60 * REFRESH_TOKEN_EXPIRES_MINUTES)
        await self.redis.setex(
            name=f"{uid}:{token}", value=json.dumps(payload), time=60 * REFRESH_TOKEN_EXPIRES_MINUTES
        )

    async def create_tokens(self, data: Dict):
        access_data = data.copy()
        refresh_data = data.copy()
        del access_data["ip_address"]
        del access_data["user_agent"]
        expire_access = (datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)).timestamp()
        expire_refresh = (
            datetime.datetime.now() + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRES_MINUTES)
        ).timestamp()
        iat = (datetime.datetime.now(datetime.timezone.utc)).timestamp()
        access_data.update(
            {
                "iat": iat,
                "exp": expire_access,
                "type": "access",
            }
        )
        refresh_data.update({"iat": iat, "exp": expire_refresh, "type": "refresh"})
        access_token = jwt.encode(access_data, settings.secret_key, algorithm=ALGORITHM)
        refresh_token = jwt.encode(refresh_data, settings.secret_key, algorithm=ALGORITHM)
        await self.put_token_to_redis(refresh_data, refresh_token)
        return {"access_token": access_token, "refresh_token": refresh_token}

    @staticmethod
    async def verify_token(token):
        try:
            payload = jwt.decode(token, key=settings.secret_key, algorithms=ALGORITHM)
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Token invalid: {str(e)}")

    async def take_new_refresh(self, token, client_ip, user_agent):
        payload = await self.verify_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        await self.check_delete_token_in_redis(token, client_ip, user_agent)
        return await self.create_tokens(payload)


async def get_token_manager():
    manager = TokenManager()
    try:
        yield manager
    finally:
        await manager.redis.aclose()
