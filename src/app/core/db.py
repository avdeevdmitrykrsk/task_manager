from uuid import uuid4

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (
    declarative_base,
    declared_attr,
    sessionmaker,
)

from app.core.config import settings


class PreBase:
    """Базовая модель для классов SQLAlchemy."""

    @declared_attr
    def __tablename__(cls):
        """Генерирует имя таблицы в lowercase."""
        return cls.__name__.lower()

    @declared_attr
    def id(cls):
        if settings.debug_mode:
            #  Для sqlite.
            return Column(
                String(36),
                primary_key=True,
                default=lambda: str(uuid4()),
                index=True,
                unique=True,
                nullable=False,
            )
        #  Для postgres.
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid4,
            index=True,
            unique=True,
            nullable=False,
        )
    created_at = Column(
        DateTime, server_default=func.now(), comment='Дата создания'
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment='Дата обновления',
    )


Base = declarative_base(cls=PreBase)
engine = create_async_engine(settings.database_url)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session():
    """Генерирует асинхронную сессию для работы с БД."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
