# Standart lib imports
from datetime import datetime
from typing import Optional

# Thirdparty imports
from pydantic import UUID4, BaseModel, ConfigDict, Field, field_validator

from app.core.constants import (
    MAX_TASK_DESCR_LENGTH,
    MAX_TASK_NAME_LENGTH,
    MIN_TASK_DESCR_LENGTH,
    MIN_TASK_NAME_LENGTH,
)

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
