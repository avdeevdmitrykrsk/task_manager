from datetime import datetime
import logging
import uuid
from typing import Generic, List, Optional, TypeVar, Union

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select

from app.core.config import settings
from app.core.db import Base
from app.schemas.task_manager import TaskFilter

logger = logging.getLogger(__name__)

ModelType = TypeVar('ModelType', bound=Base)  # type: ignore
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model):
        self.model: ModelType = model

    async def set_id_type(self, pk: Union[uuid.UUID, str]):
        """Устанавливает тип для id в зависимости от debug_mode"""

        return str(pk) if settings.debug_mode else pk

    async def get_list(
        self, session: AsyncSession, filters: TaskFilter = None
    ) -> List[Optional[ModelType]]:
        """Получает все записи по фильтру из БД"""

        query = select(self.model)
        if filters:
            logger.info('Применение фильтров списка.')
            query = filters.filter(query)

        logger.info('Выполняется получение списка.')
        result = await session.execute(query)

        logger.info('Список возвращен клиенту.')
        return result.scalars().all()

    async def get_or_404(
        self, session: AsyncSession, pk: Union[uuid.UUID, str]
    ) -> Optional[ModelType]:
        """Получает запись из БД по id либо 404"""

        logger.info(f'Установка типа для id "{pk}".')
        pk = await self.set_id_type(pk)

        logger.info(f'Попытка получения объекта с id "{pk}" из БД.')
        result = await session.execute(
            select(self.model).where(self.model.id == pk)
        )
        instance = result.scalars().first()

        if not instance:
            logger.warning(f'Объект с id "{pk}" не найден в БД.')

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Объект с id=\'{pk}\' не найден',
            )

        logger.info(f'Объект с id "{pk}" получен и возвращен клиенту.')
        return instance

    async def create(
        self,
        data: dict,
        session: AsyncSession,
    ) -> ModelType:
        """Делает запись в БД на основе полученной информации"""
        instance = self.model(**data)

        session.add(instance)
        await session.commit()
        await session.refresh(instance)

        return instance

    async def update(
        self,
        instance: ModelType,
        new_data: dict,
        session: AsyncSession,
    ) -> ModelType:
        """Обновляет запись в БД"""

        for field, value in new_data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        instance.updated_at = datetime.now()

        await session.commit()
        await session.refresh(instance)
        return instance

    async def delete(
        self,
        instance: ModelType,
        session: AsyncSession,
    ) -> None:
        """Удаляет запись из БД"""

        await session.delete(instance)
        await session.commit()

        return instance
