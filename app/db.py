from typing import Any, AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession


from core.config import settings


async_engine = create_async_engine(
    url=settings.db.url,
    echo=settings.db.echo,
    pool_size=5,
    max_overflow=100,
)
session_factory = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with session_factory() as session:
        yield session


DATABASE_URL = "mongodb://localhost:27017"
DB_NAME = "mydatabase"


async def get_db():
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DB_NAME]
    try:
        yield db
    finally:
        client.close()


# Фиктивные данные пользователей (в реальном проекте тут будет БД)
USERS_DATA = [
    {
        "username": "admin",
        "password": "$2b$12$0GvkzMFS0uoFutFZhcfYVObbWyat3Up5aWnZsCZIbxVtqGqECAqga",  # В продакшене пароли должны быть хешированы!
        "roles": ["admin"],
        "full_name": "Admin User",
        "email": "admin@example.com",
        "disabled": False,
    },
    {
        "username": "user",
        "password": "$2b$12$aBWf7Ws6gmjIg9dMwwY7s.Vne9GrSogc5hR8JU1DG2YHX.pWsdOJW",
        "roles": ["user"],
        "full_name": "Regular User",
        "email": "user@example.com",
        "disabled": False,
    },
]
resources = {
    "alice": {"content": "Секретные данные Алисы", "is_public": False},
    "user": {"content": "Секретные данные Usera", "is_public": False},
    "bob": {"content": "Публичные заметки Боба", "is_public": True},
    "admin": {"content": "Админский ресурс", "is_public": False},
}
