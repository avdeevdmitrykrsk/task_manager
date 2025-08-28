import pytest


@pytest.mark.asyncio
async def test_api_create_task(client, task_url, valid_task_data):
    result = await client.post(task_url, json=valid_task_data)
    assert result.status_code == 201


@pytest.mark.asyncio
async def test_cant_create_with_status(client, task_url, task_data_with_status):
    result = await client.post(task_url, json=task_data_with_status)
    assert result.status_code == 422
