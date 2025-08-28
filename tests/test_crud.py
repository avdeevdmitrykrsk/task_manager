import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task_manager import TaskCRUD
from app.schemas.filters import TaskFilter
from app.schemas.task_manager import CreateTaskSchema, UpdateTaskSchema


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
async def test_create_task_duplicate_name(session, create_task, task_crud):
    task = await create_task(name='Тестовая задача')

    with pytest.raises(HTTPException):
        await task_crud.create(
            {'name': task.name, 'description': task.description}, session
        )


@pytest.mark.asyncio
async def test_update_task_duplicate_name(session, create_task, task_crud):
    task = await create_task(name='Тестовая задача')
    task_2 = await create_task(name='Тестовая задача_2')

    with pytest.raises(HTTPException):
        await task_crud.update(task, {'name': task_2.name}, session)


@pytest.mark.asyncio
async def test_get_task(
    session: AsyncSession,
    task_crud: TaskCRUD,
    create_task,
):
    task = await create_task()

    fetched_task = await task_crud.get_or_404(session, pk=task.id)

    assert fetched_task.id == task.id
    assert fetched_task.name == task.name


@pytest.mark.asyncio
async def test_get_task_list(
    session: AsyncSession, task_crud: TaskCRUD, create_task
):

    task1 = await create_task()
    task2 = await create_task()
    tasks = await task_crud.get_list(session)

    assert len(tasks) == 2
    assert {task.id for task in tasks} == {task1.id, task2.id}
    assert {task.name for task in tasks} == {task1.name, task2.name}


@pytest.mark.asyncio
async def test_get_task_filtered_list(
    session: AsyncSession,
    task_crud: TaskCRUD,
    create_task,
):
    task_1 = await create_task(name='Задача 1')
    task_2 = await create_task(name='Задача 2')

    first_filter = TaskFilter(name=task_1.name)
    second_filter = TaskFilter(name=task_2.name)

    first_tasks_list = await task_crud.get_list(session, first_filter)
    assert len(first_tasks_list) == 1
    assert first_tasks_list[0].name == task_1.name

    second_tasks_list = await task_crud.get_list(session, second_filter)
    assert len(second_tasks_list) == 1
    assert second_tasks_list[0].name == task_2.name


@pytest.mark.asyncio
async def test_patch_task(
    session: AsyncSession,
    task_crud: TaskCRUD,
    new_valid_task_data: dict,
    create_task,
):

    task = await create_task()

    new_task_data = UpdateTaskSchema(**new_valid_task_data)
    updated_task = await task_crud.update(
        task,
        new_task_data.model_dump(exclude_unset=True, exclude_none=True),
        session,
    )

    assert updated_task.name == new_valid_task_data['name']
    assert updated_task.description == new_valid_task_data['description']


@pytest.mark.asyncio
async def test_delete_task(
    session: AsyncSession,
    task_crud: TaskCRUD,
    create_task,
):
    task = await create_task()
    await task_crud.delete(task, session)

    with pytest.raises(HTTPException) as exc:
        await task_crud.get_or_404(session, task.id)
    assert exc.value.status_code == 404
