import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .fixtures import *  # noqa
from app.core.base import Base
from app.core.db import get_async_session

TEST_DATABASE_URL = 'sqlite+aiosqlite:///./pytest.db'

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session():
    async with TestSessionLocal() as async_session:
        yield async_session


@pytest_asyncio.fixture
async def client(session):
    from app.main import app

    async def override_db():
        yield session

    app.dependency_overrides = {}
    app.dependency_overrides[get_async_session] = override_db

    async with AsyncClient(transport=ASGITransport(app=app)) as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def event_loop():
    import asyncio

    loop = asyncio.get_event_loop()
    yield loop
