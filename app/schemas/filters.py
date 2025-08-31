from enum import Enum
from typing import Optional

from fastapi import HTTPException, Query, Request
from fastapi import status as http_status
from fastapi_filter.contrib.sqlalchemy import Filter

from app.models.task_manager import Task


class TaskStatus(str, Enum):

    CREATED = 'Создано'
    IN_PROGRESS = 'В работе'
    COMPLETED = 'Завершено'


class TaskFilter(Filter):
    status: Optional[TaskStatus] = None
    name: Optional[str] = None
    description: Optional[str] = None

    class Constants:
        model = Task
        ordering_field_name = 'created_at'
        search_field_name = None


async def validate_filters(
    request: Request,
    status: Optional[TaskStatus] = Query(None),
    name: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
) -> TaskFilter:
    allowed_params = {
        'status',
        'name',
        'description',
    }
    query_params = set(request.query_params.keys())

    extra_params = query_params - allowed_params
    if extra_params:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'Недопустимые параметры: "{extra_params}"',
        )

    return TaskFilter(
        status=status,
        name=name,
        description=description,
    )
