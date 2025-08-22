from typing import Dict
import jwt
import datetime
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import bcrypt
from core.config import settings, mini_db

bcrypt.__about__ = bcrypt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 1
REFRESH_TOKEN_EXPIRES_MINUTES = 3

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ROLES_DICT = {1: "admin", 2: "user", 3: "guest"}


async def create_tokens(data: Dict):
    access_data = data.copy()
    refresh_data = data.copy()
    expire_access = datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    expire_refresh = datetime.datetime.now() + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRES_MINUTES)
    access_data.update({"exp": expire_access, "type": "access"})
    refresh_data.update({"exp": expire_refresh, "type": "refresh"})
    access_token = jwt.encode(access_data, settings.secret_key, algorithm=ALGORITHM)
    refresh_token = jwt.encode(refresh_data, settings.secret_key, algorithm=ALGORITHM)
    mini_db.append({data["sub"]: refresh_token})
    return {"access_token": access_token, "refresh_token": refresh_token}


async def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
