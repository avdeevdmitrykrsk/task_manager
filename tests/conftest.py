import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.base import Base
from app.core.config import settings
from app.core.db import get_async_session

from .fixtures import *  # noqa

load_dotenv()


# def get_databse_url():
#     return (
#         f'postgresql+asyncpg://'
#         f'{settings.postgres_user}:{settings.postgres_password}'
#         f'@localhost:{settings.db_port}/{settings.postgres_db}'
#         if settings.debug_mode == 'docker'
#         else 'sqlite+aiosqlite:///./pytest.db'
#     )


@pytest.fixture(scope='session', autouse=True)
def engine():
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        poolclass=NullPool,
    )
    return engine


@pytest_asyncio.fixture(autouse=True)
async def init_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        try:
            yield session
            await session.rollback()
        finally:
            await session.close()
            async with engine.begin() as conn:
                for table in reversed(Base.metadata.sorted_tables):
                    await conn.execute(table.delete())


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
