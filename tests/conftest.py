from typing import AsyncGenerator

import pytest
import redis.asyncio as redis
from core.config import settings
from db import get_session
from fastapi_limiter import FastAPILimiter
from httpx import ASGITransport, AsyncClient
from models import Base
from models import Todo as TodoModel
from models import User as UserModel
from models.user import UserRoleEnum
from security import crypt_context
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app

test_engine = create_async_engine(
    url=settings.db.test_url,
    echo=False,
    poolclass=NullPool,
)
test_factory = async_sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_factory() as session:
        yield session


app.dependency_overrides[get_session] = override_get_async_session


async def add_metadata(session):
    user = UserModel(username="testuser", email="test@example.com", password=crypt_context.hash("testpass"))
    user2 = UserModel(
        username="admin",
        email="test@example.com",
        password=crypt_context.hash("admin"),
        role=UserRoleEnum.admin,
    )
    todo1 = TodoModel(title="test todo", description="test todo description", completed=False, user_id=1)
    todo2 = TodoModel(title="test two", description="test two  todo description", completed=False, user_id=2)
    session.add(user)
    session.add(user2)
    await session.commit()
    await session.refresh(user)
    await session.refresh(user2)
    session.add(todo1)
    session.add(todo2)

    await session.commit()
    await session.refresh(user)
    await session.refresh(user2)


@pytest.fixture(scope="function")
async def client():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with test_factory() as session:
        await add_metadata(session)
    con = redis.Redis(host="127.0.0.1")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        await FastAPILimiter.init(con)
        yield ac
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def empty_db_client():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    con = redis.Redis(host="127.0.0.1")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        await FastAPILimiter.init(con)
        yield ac
