from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.app.core.db import Base
from src.app.crud.base import CRUDBase
from src.app.crud.task_manager import Task, TaskCRUD
from src.app.main import app

TEST_DATABASE_URL = 'sqlite+aiosqlite:///./pytest.db'

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope='session')
def event_loop():
    import asyncio

    loop = asyncio.get_event_loop()
    yield loop


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Task.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Task.metadata.drop_all)


@pytest_asyncio.fixture
async def session():
    async with AsyncSessionLocal() as async_session:
        yield async_session


@pytest.fixture
def task_crud(mocker):
    mock_manager = mocker.patch(
        'src.app.crud.task_manager.ConnectionManager',
        new_callable=AsyncMock,
    )
    return TaskCRUD(Task, manager=mock_manager)


@pytest_asyncio.fixture
async def valid_task_data():
    return {
        'name': 'Тестовая задача',
        'description': 'Тестовое описание'
    }


@pytest_asyncio.fixture
async def new_valid_task_data():
    return {
        'name': 'Обновленное имя',
        'description': 'Обновленное описание'
    }


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
