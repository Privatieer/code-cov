from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.src.domain.entities.models import Task, Attachment, TaskStatus, TaskPriority, Checklist, ChecklistItem
from backend.src.domain.ports.repositories.base import ITaskRepository
from backend.src.infrastructure.persistence.sqlalchemy.models.schema import (
    TaskModel, AttachmentModel, ChecklistModel, ChecklistItemModel
)
from datetime import datetime, timedelta

class SQLAlchemyTaskRepository(ITaskRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: TaskModel) -> Task:
        if not model:
            return None
        return Task(
            id=model.id,
            user_id=model.user_id,
            task_list_id=model.task_list_id,
            title=model.title,
            description=model.description,
            status=TaskStatus(model.status),
            priority=TaskPriority(model.priority),
            due_date=model.due_date,
            tags=model.tags or [],
            created_at=model.created_at,
            updated_at=model.updated_at,
            attachments=[
                Attachment(
                    id=a.id,
                    task_id=a.task_id,
                    filename=a.filename,
                    file_url=a.file_url,
                    file_size_bytes=a.file_size_bytes,
                    content_type=a.content_type,
                    created_at=a.created_at
                ) for a in model.attachments
            ],
            checklists=[
                Checklist(
                    id=c.id,
                    task_id=c.task_id,
                    title=c.title,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                    items=[
                        ChecklistItem(
                            id=i.id,
                            checklist_id=i.checklist_id,
                            content=i.content,
                            is_completed=i.is_completed,
                            position=i.position,
                            created_at=i.created_at
                        ) for i in sorted(c.items, key=lambda x: (x.position, x.created_at))
                    ]
                ) for c in model.checklists
            ]
        )

    def _to_model(self, entity: Task) -> TaskModel:
        return TaskModel(
            id=entity.id,
            user_id=entity.user_id,
            task_list_id=entity.task_list_id,
            title=entity.title,
            description=entity.description,
            status=entity.status.value,
            priority=entity.priority.value,
            due_date=entity.due_date,
            tags=entity.tags,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        query = (
            select(TaskModel)
            .options(
                selectinload(TaskModel.attachments),
                selectinload(TaskModel.checklists).selectinload(ChecklistModel.items)
            )
            .where(TaskModel.id == task_id)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model)

    async def list_by_user(
        self, 
        user_id: UUID, 
        filters: dict = None, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Task]:
        query = (
            select(TaskModel)
            .options(
                selectinload(TaskModel.attachments),
                selectinload(TaskModel.checklists).selectinload(ChecklistModel.items)
            )
            .where(TaskModel.user_id == user_id)
        )
        
        if filters:
            if "status" in filters and filters["status"]:
                query = query.where(TaskModel.status == filters["status"])
            if "priority" in filters and filters["priority"]:
                query = query.where(TaskModel.priority == filters["priority"])
            if "task_list_id" in filters and filters["task_list_id"]:
                query = query.where(TaskModel.task_list_id == filters["task_list_id"])
            # Add other filters here...

        query = query.limit(limit).offset(offset).order_by(TaskModel.created_at.desc())
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def create(self, task: Task) -> Task:
        model = self._to_model(task)
        self.session.add(model)
        # Handle attachments if any are pre-populated (rare in create, but possible)
        for att in task.attachments:
            att_model = AttachmentModel(
                id=att.id,
                task_id=model.id,
                filename=att.filename,
                file_url=att.file_url,
                file_size_bytes=att.file_size_bytes,
                content_type=att.content_type,
                created_at=att.created_at
            )
            self.session.add(att_model)
            
        await self.session.commit()
        # Refresh to get DB-assigned fields if any (like timestamps, though we set them)
        return await self.get_by_id(task.id)

    async def update(self, task: Task) -> Task:
        # In a full implementation, we'd fetch the existing model and update fields.
        # For simplicity, we assume the Task entity is the source of truth.
        # However, usually we merge.
        query = select(TaskModel).where(TaskModel.id == task.id)
        result = await self.session.execute(query)
        existing_model = result.scalar_one_or_none()
        
        if existing_model:
            existing_model.task_list_id = task.task_list_id
            existing_model.title = task.title
            existing_model.description = task.description
            existing_model.status = task.status.value
            existing_model.priority = task.priority.value
            existing_model.due_date = task.due_date
            existing_model.tags = task.tags
            existing_model.updated_at = datetime.utcnow()
            
            await self.session.commit()
            return await self.get_by_id(task.id)
        return None

    async def delete(self, task_id: UUID) -> bool:
        # Use ORM delete to respect cascade relationships
        query = select(TaskModel).where(TaskModel.id == task_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False

    async def add_attachment(self, attachment: Attachment) -> Attachment:
        att_model = AttachmentModel(
            id=attachment.id,
            task_id=attachment.task_id,
            filename=attachment.filename,
            file_url=attachment.file_url,
            file_size_bytes=attachment.file_size_bytes,
            content_type=attachment.content_type,
            created_at=attachment.created_at,
        )
        self.session.add(att_model)
        await self.session.commit()
        await self.session.refresh(att_model)
        # Convert back to domain model to return, though not strictly necessary
        # as the input is already the complete domain model.
        return attachment
        
    async def get_attachment_by_id(self, attachment_id: UUID) -> Optional[Attachment]:
        query = select(AttachmentModel).where(AttachmentModel.id == attachment_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return Attachment(
            id=model.id,
            task_id=model.task_id,
            filename=model.filename,
            file_url=model.file_url,
            file_size_bytes=model.file_size_bytes,
            content_type=model.content_type,
            created_at=model.created_at
        )

    async def delete_attachment(self, attachment_id: UUID) -> bool:
        # Use ORM delete for consistency
        query = select(AttachmentModel).where(AttachmentModel.id == attachment_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False

    async def get_due_soon(self, hours: int = 24) -> List[Task]:
        cutoff = datetime.utcnow() + timedelta(hours=hours)
        now = datetime.utcnow()
        
        query = select(TaskModel).options(selectinload(TaskModel.attachments)).where(
            TaskModel.due_date <= cutoff,
            TaskModel.due_date > now,
            TaskModel.status != "done"
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

