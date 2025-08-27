import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.crud.task_manager import TaskCRUD
from src.app.schemas.task_manager import CreateTaskSchema, UpdateTaskSchema


@pytest.mark.asyncio
async def test_create_task(
    session: AsyncSession, task_crud: TaskCRUD, valid_task_data
):
    task_data = CreateTaskSchema(**valid_task_data)
    created_task = await task_crud.create(
        data=task_data.model_dump(), session=session
    )

    assert created_task.name == valid_task_data['name']
    assert created_task.description == valid_task_data['description']
    assert created_task.status == 'Создано'
    assert created_task.id is not None


@pytest.mark.asyncio
async def test_get_task(
    session: AsyncSession, task_crud: TaskCRUD, valid_task_data: dict
):
    task_data = CreateTaskSchema(**valid_task_data)
    created_task = await task_crud.create(
        data=task_data.model_dump(), session=session
    )

    fetched_task = await task_crud.get_or_404(session, pk=created_task.id)

    assert fetched_task.id == created_task.id
    assert fetched_task.name == created_task.name


@pytest.mark.asyncio
async def test_get_task_list(
    session: AsyncSession,
    task_crud: TaskCRUD,
    valid_task_data: dict,
    valid_task_data2: dict,
):
    task1_data = CreateTaskSchema(**valid_task_data)
    task2_data = CreateTaskSchema(**valid_task_data2)

    task1 = await task_crud.create(
        data=task1_data.model_dump(), session=session
    )
    task2 = await task_crud.create(
        data=task2_data.model_dump(), session=session
    )

    tasks = await task_crud.get_list(session)

    assert len(tasks) == 2
    assert {task.id for task in tasks} == {task1.id, task2.id}
    assert {task.name for task in tasks} == {task1.name, task2.name}


@pytest.mark.asyncio
async def test_patch_task(
    session: AsyncSession,
    task_crud: TaskCRUD,
    valid_task_data: dict,
    new_valid_task_data: dict,
):

    task_data = CreateTaskSchema(**valid_task_data)
    created_task = await task_crud.create(
        data=task_data.model_dump(), session=session
    )

    new_task_data = UpdateTaskSchema(**new_valid_task_data)
    updated_task = await task_crud.update(
        created_task,
        new_task_data.model_dump(exclude_unset=True, exclude_none=True),
        session,
    )

    assert updated_task.name == new_valid_task_data['name']
    assert updated_task.description == new_valid_task_data['description']
