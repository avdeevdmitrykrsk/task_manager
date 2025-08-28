# Standart lib imports
from datetime import datetime
from enum import Enum
from typing import Optional

# Thirdparty imports
from fastapi import HTTPException, Query, Request
from fastapi import status as http_status
from pydantic import UUID4, BaseModel, ConfigDict, Field, field_validator

from app.core.constants import (
    MAX_TASK_DESCR_LENGTH,
    MAX_TASK_NAME_LENGTH,
    MIN_TASK_DESCR_LENGTH,
    MIN_TASK_NAME_LENGTH,
)
from app.schemas.filters import TaskFilter, TaskStatus

TASK_STATUSES = ('создано', 'в работе', 'завершено')


class CreateTaskSchema(BaseModel):
    name: str = Field(
        ..., min_length=MIN_TASK_NAME_LENGTH, max_length=MAX_TASK_NAME_LENGTH
    )
    description: str = Field(
        ..., min_length=MIN_TASK_DESCR_LENGTH, max_length=MAX_TASK_DESCR_LENGTH
    )

    model_config = ConfigDict(extra='forbid')


class GetTaskSchema(BaseModel):
    """Pydantic-схема для получения task"""

    id: UUID4
    name: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpdateTaskSchema(BaseModel):

    name: Optional[str] = Field(None, max_length=MAX_TASK_NAME_LENGTH)
    description: Optional[str] = Field(None)
    status: Optional[str] = Field(None)

    model_config = ConfigDict(extra='forbid')

    @field_validator('status')
    @classmethod
    def validate_status(cls, value: Optional[str]):
        valid_statuses = TASK_STATUSES

        if value and value.lower() not in valid_statuses:
            raise ValueError(
                f'{value} - недопустимый статус, '
                f'выберите из: {" -- ".join(valid_statuses)}'
            )
        return value


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
            detail=f'Недопустимые параметры: {extra_params}',
        )

    return TaskFilter(
        status=status,
        name=name,
        description=description,
    )
