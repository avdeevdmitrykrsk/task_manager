from uuid import UUID
from sqlalchemy import CheckConstraint, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.core.config import settings
from app.core.constants import MAX_TASK_NAME_LENGTH, MAX_TASK_STATUS_LENGTH
from app.core.db import Base


class Task(Base):

    name = Column(
        String(MAX_TASK_NAME_LENGTH),
        unique=True,
        nullable=False,
        comment='Название задачи',
    )
    description = Column(
        Text(), nullable=False, comment='Описание задачи'
    )
    status = Column(
        String(MAX_TASK_STATUS_LENGTH),
        index=True,
        default='Создано',
        nullable=False,
        server_default='Создано',
        comment='Статус выполнения задачи',
    )

    __table_args__ = (
        CheckConstraint(
            status.in_(['Создано', 'В работе', 'Завершено']),
            name='check_status',
        ),
    )
