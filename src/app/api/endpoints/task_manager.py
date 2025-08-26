import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud.task_manager import TaskCRUD, get_task_crud
from app.models.task_manager import Task
from app.schemas.task_manager import (
    CreateTaskSchema,
    GetTaskSchema,
    TaskFilter,
    # TaskFilterSchema,
    UpdateTaskSchema,
    validate_filters,
)

router = APIRouter(prefix='/tasks')
logger = logging.getLogger(__name__)


@router.get(
    '/{task_id}',
    response_model=GetTaskSchema,
    summary='Получение задачи',
    description='Получает задачу по id',
)
async def get_task(
    task_id: uuid.UUID,
    task_crud: TaskCRUD = Depends(get_task_crud),
    session: AsyncSession = Depends(get_async_session),
) -> Task:

    logger.info(f'Подготовка к получению объекта с id "{task_id}".')
    return await task_crud.get_or_404(session=session, pk=task_id)


@router.get(
    '/',
    response_model=List[GetTaskSchema],
    summary='Получение списка задач',
    description='Получает список всех задач',
)
async def get_tasks_list(
    filters: TaskFilter = Depends(validate_filters),
    task_crud: TaskCRUD = Depends(get_task_crud),
    session: AsyncSession = Depends(get_async_session),
) -> Optional[List[Task]]:

    logger.info('Подготовка к получению списка объектов из БД.')
    return await task_crud.get_list(session=session, filters=filters)


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=GetTaskSchema,
    summary='Создание задачи',
    description='Создает задачу',
)
async def create_task(
    task_data: CreateTaskSchema,
    task_crud: TaskCRUD = Depends(get_task_crud),
    session: AsyncSession = Depends(get_async_session),
) -> GetTaskSchema:

    data = task_data.model_dump()
    await task_crud.check_unique_name(session=session, name=data['name'])

    return await task_crud.create(session=session, data=data)


@router.patch(
    '/{task_id}',
    response_model=GetTaskSchema,
    summary='Обновление задачи',
    description='Обновляет данные задачи',
)
async def update_task(
    task_id: uuid.UUID,
    new_task_data: UpdateTaskSchema,
    task_crud: TaskCRUD = Depends(get_task_crud),
    session: AsyncSession = Depends(get_async_session),
) -> Task:

    instance = await task_crud.get_or_404(session=session, pk=task_id)
    validated_data = await task_crud.validate_before_update(
        session, new_task_data.model_dump(exclude_unset=True)
    )

    return await task_crud.update(
        session=session, instance=instance, new_data=validated_data
    )


@router.delete(
    '/{task_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary='Удаление задачи',
    description='Удаляет задачу по id',
)
async def delete_task(
    task_id: uuid.UUID,
    task_crud: TaskCRUD = Depends(get_task_crud),
    session: AsyncSession = Depends(get_async_session),
):
    instance = await task_crud.get_or_404(session=session, pk=task_id)
    await task_crud.delete(session=session, instance=instance)
