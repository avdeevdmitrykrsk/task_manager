from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.websocket import (
    ConnectionManager,
    get_connection_manager,
)
from app.crud.base import CRUDBase
from app.models.task_manager import Task
from app.schemas.task_manager import CreateTaskSchema, UpdateTaskSchema


class TaskCRUD(CRUDBase[Task, CreateTaskSchema, UpdateTaskSchema]):

    def __init__(self, model, manager: ConnectionManager):
        super().__init__(model)
        self.connection_manager = manager

    def is_valid_status_transition(self, old: str, new: str) -> bool:
        transitions = {
            'Создано': ['В работе'],
            'В работе': ['Завершено'],
            'Завершено': ['В работе'],
        }
        return new in transitions.get(old)

    async def _generate_br_data(self, instance: Task) -> dict:
        return {
            'data': {
                'id': str(instance.id),
                'name': instance.name,
                'status': instance.status,
                'description': instance.description,
                'updated_at': instance.updated_at.isoformat(),
            },
        }

    async def update(
        self,
        instance: Task,
        new_data: dict,
        session: AsyncSession,
    ) -> Task:

        if 'name' in new_data:
            await self.check_unique_name(
                session, name=new_data['name'], exclude_id=instance.id
            )

        if 'status' in new_data:
            old_status = instance.status
            new_status = new_data['status']

            if not self.is_valid_status_transition(old_status, new_status):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Недопустимый переход статуса: '
                    f'{old_status} -> {new_status}',
                )

        updated_task: Task = await super().update(
            instance=instance,
            new_data=new_data,
            session=session,
        )

        br_data = await self._generate_br_data(updated_task)
        br_data['event'] = 'task_updated'
        await self.connection_manager.broadcast(br_data)

        return updated_task

    async def create(
        self,
        data: dict,
        session: AsyncSession,
    ) -> Task:

        await self.check_unique_name(session, name=data['name'])

        new_task = await super().create(data=data, session=session)

        br_data = await self._generate_br_data(new_task)
        br_data['event'] = 'task_created'
        await self.connection_manager.broadcast(br_data)

        return new_task

    async def delete(
        self,
        instance: Task,
        session: AsyncSession,
    ) -> None:
        deleted_task = await super().delete(instance=instance, session=session)

        br_data = await self._generate_br_data(deleted_task)
        br_data['event'] = 'task_deleted'
        await self.connection_manager.broadcast(br_data)

    async def check_unique_name(
        self,
        session: AsyncSession,
        name: str,
        exclude_id: Optional[str] = None,
    ) -> None:

        query = select(self.model).where(
            func.lower(self.model.name) == func.lower(name)
        )

        if exclude_id is not None:
            query = query.where(self.model.id != exclude_id)

        result = await session.execute(query)
        db_obj = result.scalars().first()

        if db_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Имя \'{name}\' недоступно.',
            )


def get_task_crud(
    manager: ConnectionManager = Depends(get_connection_manager),
) -> TaskCRUD:
    return TaskCRUD(model=Task, manager=manager)
