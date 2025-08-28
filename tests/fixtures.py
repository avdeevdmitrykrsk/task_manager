from random import choices
from string import ascii_letters, digits
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task_manager import Task, TaskCRUD
from app.schemas.task_manager import CreateTaskSchema


@pytest.fixture
def task_crud(mocker):
    mock_manager = mocker.patch(
        'app.crud.task_manager.ConnectionManager',
        new_callable=AsyncMock,
    )
    return TaskCRUD(Task, manager=mock_manager)


@pytest_asyncio.fixture
async def valid_task_data():
    return {'name': 'Тестовая задача', 'description': 'Тестовое описание'}


@pytest_asyncio.fixture
async def valid_task_data2():
    return {'name': 'Тестовая задача2', 'description': 'Тестовое описание2'}


@pytest_asyncio.fixture
async def task_data_with_status():
    return {
        'name': 'Тестовая задача',
        'description': 'Тестовое описание',
        'status': 'В работе',
    }


@pytest_asyncio.fixture
async def new_valid_task_data():
    return {'name': 'Обновленное имя', 'description': 'Обновленное описание'}


@pytest_asyncio.fixture
async def task_url():
    return 'http://127.0.0.1:8000/api/tasks/'


@pytest_asyncio.fixture
async def create_task(session: AsyncSession, task_crud: TaskCRUD):
    created_tasks = []

    async def _create_task(**kwargs):
        variable_string = ascii_letters + digits
        defaults = {
            'name': ''.join(choices(variable_string, k=10)),
            'description': ''.join(choices(variable_string, k=100)),
        }
        defaults.update(kwargs)
        schema = CreateTaskSchema(**defaults)

        task = await task_crud.create(
            data=schema.model_dump(), session=session
        )

        created_tasks.append(task)

        return task

    yield _create_task

    for task in created_tasks:
        await session.delete(task)
    await session.commit()
