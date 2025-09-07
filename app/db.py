from typing import Any, AsyncGenerator

from core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

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


resources = {
    "alice": {"content": "Секретные данные Алисы", "is_public": False},
    "user": {"content": "Секретные данные Usera", "is_public": False},
    "bob": {"content": "Публичные заметки Боба", "is_public": True},
    "admin": {"content": "Админский ресурс", "is_public": False},
}
