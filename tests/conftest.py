from typing import AsyncGenerator

from fastapi_limiter import FastAPILimiter
from httpx import AsyncClient, ASGITransport
from sqlalchemy import  NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app  # Предполагается, что объект app объявлен в app/main.py
import pytest
from core.config import settings
from db import get_session, session_factory
from models import Base, User as UserModel
from models.user import UserRoleEnum
from security import crypt_context
import redis.asyncio as redis
test_engine = create_async_engine(
    url=settings.db.test_url,
    echo=False,
    poolclass=NullPool,
)
test_factory =async_sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_factory() as session:
        yield session

app.dependency_overrides[get_session] = override_get_async_session


@pytest.fixture(scope="session",autouse=True)
async def test_lifespan():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with test_factory() as session:
        user = UserModel(
            username='testuser',
            email='test@example.com',
            password=crypt_context.hash('testpass')
        )
        user2 = UserModel(
            username='admin',
            email='test@example.com',
            password=crypt_context.hash('admin'),
            role=UserRoleEnum.admin,

        )
        session.add(user)
        session.add(user2)

        await session.commit()
        await session.refresh(user)
        await session.refresh(user2)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)





@pytest.fixture(scope="function")
async def client():
    con = redis.Redis(host="127.0.0.1")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        await FastAPILimiter.init(con)
        yield ac

