from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.src.domain.entities.models import Checklist, ChecklistItem
from backend.src.domain.ports.repositories.base import IChecklistRepository
from backend.src.infrastructure.persistence.sqlalchemy.models.schema import ChecklistModel, ChecklistItemModel

class SQLAlchemyChecklistRepository(IChecklistRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_checklist(self, checklist: Checklist) -> Checklist:
        model = ChecklistModel(
            id=checklist.id,
            task_id=checklist.task_id,
            title=checklist.title,
            created_at=checklist.created_at,
            updated_at=checklist.updated_at
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        # Eagerly load items relationship (even if empty) to avoid greenlet error
        query = (
            select(ChecklistModel)
            .where(ChecklistModel.id == checklist.id)
            .options(selectinload(ChecklistModel.items))
        )
        result = await self.session.execute(query)
        model_with_items = result.scalar_one()
        # Sort items by position to maintain order
        model_with_items.items = sorted(model_with_items.items, key=lambda x: (x.position, x.created_at))
        return Checklist.model_validate(model_with_items)

    async def get_checklist_by_id(self, checklist_id: UUID) -> Optional[Checklist]:
        query = (
            select(ChecklistModel)
            .where(ChecklistModel.id == checklist_id)
            .options(selectinload(ChecklistModel.items))
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model:
            # Sort items by position to maintain order
            model.items = sorted(model.items, key=lambda x: (x.position, x.created_at))
            return Checklist.model_validate(model)
        return None

    async def delete_checklist(self, checklist_id: UUID) -> bool:
        # Use ORM delete to respect cascade relationships (items will be deleted automatically)
        query = select(ChecklistModel).where(ChecklistModel.id == checklist_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False

    async def add_item(self, item: ChecklistItem) -> ChecklistItem:
        model = ChecklistItemModel(
            id=item.id,
            checklist_id=item.checklist_id,
            content=item.content,
            is_completed=item.is_completed,
            position=item.position,
            created_at=item.created_at
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return ChecklistItem.model_validate(model)

    async def update_item(self, item: ChecklistItem) -> ChecklistItem:
        query = select(ChecklistItemModel).where(ChecklistItemModel.id == item.id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model:
            model.content = item.content
            model.is_completed = item.is_completed
            model.position = item.position
            await self.session.commit()
            await self.session.refresh(model)
            return ChecklistItem.model_validate(model)
        return item

    async def delete_item(self, item_id: UUID) -> bool:
        # Use ORM delete
        query = select(ChecklistItemModel).where(ChecklistItemModel.id == item_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False

    async def get_item_by_id(self, item_id: UUID) -> Optional[ChecklistItem]:
        query = select(ChecklistItemModel).where(ChecklistItemModel.id == item_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model:
            return ChecklistItem.model_validate(model)
        return None

