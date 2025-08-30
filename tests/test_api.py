import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task_manager import TaskCRUD


@pytest.mark.asyncio
async def test_get_task(
    client: AsyncClient,
    task_url: str,
    create_task,
):
    task = await create_task()
    result = await client.get(f'{task_url}{task.id}')

    assert result.status_code == status.HTTP_200_OK

    data: dict = result.json()
    expected_fields = {
        'name',
        'description',
        'status',
        'created_at',
        'updated_at',
        'id',
    }
    assert set(data) == expected_fields

    assert data['id'] == str(task.id)
    assert data['name'] == task.name
    assert data['status'] == 'Создано'


@pytest.mark.asyncio
async def test_get_tasks_list_also_filtered(
    client: AsyncClient,
    task_url: str,
    create_task,
    task_crud: TaskCRUD,
    session: AsyncSession,
):

    await create_task()
    task = await create_task(name='Тестовая задача2')

    in_work_task = await task_crud.update(
        task, {'status': 'В работе'}, session
    )

    result = await client.get(task_url)
    all_data = result.json()

    assert result.status_code == status.HTTP_200_OK
    assert isinstance(all_data, list)
    assert len(result.json()) == 2

    result = await client.get(task_url, params={'status': 'В работе'})
    all_data = result.json()

    assert len(all_data) == 1

    data = all_data[0]

    assert data['id'] == str(in_work_task.id)
    assert data['status'] == 'В работе'


@pytest.mark.asyncio
async def test_update_task_status_transitions(
    task_url: str, client: AsyncClient, create_task
):
    task = await create_task()
    result = await client.patch(
        f'{task_url}{task.id}', json={'status': 'В работе'}
    )

    assert result.status_code == status.HTTP_200_OK
    assert result.json()['status'] == 'В работе'

    task_2 = await create_task()
    result = await client.patch(
        f'{task_url}{task_2.id}', json={'status': 'Завершено'}
    )

    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Недопустимый переход' in result.json()['detail']


@pytest.mark.asyncio
async def test_create_task(
    client: AsyncClient, task_url: str, valid_task_data: dict
):
    result = await client.post(task_url, json=valid_task_data)
    assert result.status_code == status.HTTP_201_CREATED

    data: dict = result.json()

    assert data['name'] == valid_task_data['name']
    assert data['description'] == valid_task_data['description']
    assert data['status'] == 'Создано'


@pytest.mark.asyncio
async def test_cant_create_with_status(
    client: AsyncClient, task_url: str, task_data_with_status: dict
):
    result = await client.post(task_url, json=task_data_with_status)
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    data: dict = result.json()

    assert any(
        error.get('loc') == ['body', 'status']
        and error.get('type') == 'extra_forbidden'
        for error in data.get('detail')
    )


@pytest.mark.asyncio
async def test_update_task(
    client: AsyncClient,
    task_url: str,
    new_valid_task_data: dict,
    create_task,
):
    task = await create_task()

    result = await client.patch(
        f'{task_url}{task.id}', json=new_valid_task_data
    )
    assert result.status_code == status.HTTP_200_OK

    data = result.json()

    assert data['id'] == str(task.id)
    assert data['name'] == new_valid_task_data['name']
    assert data['description'] == new_valid_task_data['description']
    assert data['status'] == new_valid_task_data['status']


@pytest.mark.asyncio
async def test_delete_task(task_url: str, client: AsyncClient, create_task):
    task = await create_task()

    result = await client.delete(f'{task_url}{task.id}')
    assert result.status_code == status.HTTP_204_NO_CONTENT

    result = await client.get(f'{task_url}{task.id}')
    assert result.status_code == status.HTTP_404_NOT_FOUND
