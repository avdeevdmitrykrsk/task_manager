from enum import Enum
from typing import Optional

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
