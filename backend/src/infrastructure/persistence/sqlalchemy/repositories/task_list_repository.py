from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.src.domain.entities.models import TaskList
from backend.src.domain.ports.repositories.base import ITaskListRepository
from backend.src.infrastructure.persistence.sqlalchemy.models.schema import TaskListModel

class SQLAlchemyTaskListRepository(ITaskListRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, task_list_id: UUID) -> Optional[TaskList]:
        query = select(TaskListModel).where(TaskListModel.id == task_list_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model:
            return TaskList.model_validate(model)
        return None

    async def create(self, task_list: TaskList) -> TaskList:
        model = TaskListModel(
            id=task_list.id,
            user_id=task_list.user_id,
            name=task_list.name,
            created_at=task_list.created_at,
            updated_at=task_list.updated_at
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return TaskList.model_validate(model)

    async def list_by_user(self, user_id: UUID) -> List[TaskList]:
        query = select(TaskListModel).where(TaskListModel.user_id == user_id).order_by(TaskListModel.created_at)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [TaskList.model_validate(m) for m in models]

    async def update(self, task_list: TaskList) -> TaskList:
        query = select(TaskListModel).where(TaskListModel.id == task_list.id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model:
            model.name = task_list.name
            model.updated_at = task_list.updated_at
            await self.session.commit()
            await self.session.refresh(model)
            return TaskList.model_validate(model)
        return task_list

    async def delete(self, task_list_id: UUID) -> bool:
        query = delete(TaskListModel).where(TaskListModel.id == task_list_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

