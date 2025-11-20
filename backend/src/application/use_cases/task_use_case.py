from typing import List, Optional
from uuid import UUID
from backend.src.domain.entities.models import Task
from backend.src.domain.ports.repositories.base import ITaskRepository, IFileStorage, ITaskListRepository
from backend.src.application.dtos.task_dtos import TaskCreateDTO, TaskUpdateDTO, TaskResponseDTO
from backend.src.domain.entities.models import Attachment

class TaskUseCase:
    def __init__(
        self, 
        task_repo: ITaskRepository, 
        file_storage: IFileStorage,
        task_list_repo: Optional[ITaskListRepository] = None
    ):
        self.task_repo = task_repo
        self.file_storage = file_storage
        self.task_list_repo = task_list_repo

    async def create_task(self, user_id: UUID, dto: TaskCreateDTO) -> Task:
        # Verify task_list ownership if provided
        if dto.task_list_id and self.task_list_repo:
            task_list = await self.task_list_repo.get_by_id(dto.task_list_id)
            if not task_list or task_list.user_id != user_id:
                raise ValueError("Invalid task list ID")

        task = Task(
            user_id=user_id,
            task_list_id=dto.task_list_id,
            title=dto.title,
            description=dto.description,
            priority=dto.priority,
            due_date=dto.due_date,
            tags=dto.tags
        )
        return await self.task_repo.create(task)

    async def get_user_tasks(
        self, 
        user_id: UUID, 
        filters: dict, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Task]:
        return await self.task_repo.list_by_user(user_id, filters, limit, offset)

    async def get_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        task = await self.task_repo.get_by_id(task_id)
        if task and task.user_id == user_id:
            return task
        return None

    async def update_task(self, task_id: UUID, user_id: UUID, dto: TaskUpdateDTO) -> Optional[Task]:
        task = await self.get_task(task_id, user_id)
        if not task:
            return None

        # Verify task_list ownership if changing
        if dto.task_list_id and self.task_list_repo:
             task_list = await self.task_list_repo.get_by_id(dto.task_list_id)
             if not task_list or task_list.user_id != user_id:
                 raise ValueError("Invalid task list ID")
             task.task_list_id = dto.task_list_id

        if dto.title is not None:
            task.title = dto.title
        if dto.description is not None:
            task.description = dto.description
        if dto.status is not None:
            task.status = dto.status
        if dto.priority is not None:
            task.priority = dto.priority
        if dto.due_date is not None:
            task.due_date = dto.due_date
        if dto.tags is not None:
            task.tags = dto.tags

        return await self.task_repo.update(task)

    async def delete_task(self, task_id: UUID, user_id: UUID) -> bool:
        task = await self.get_task(task_id, user_id)
        if not task:
            return False
            
        # Delete attachments from storage
        for attachment in task.attachments:
            await self.file_storage.delete(attachment.file_url)
            
        return await self.task_repo.delete(task_id)

    async def add_attachment(
        self, 
        task_id: UUID, 
        user_id: UUID, 
        file_content: bytes, 
        filename: str, 
        content_type: str
    ) -> Optional[Task]:
        task = await self.get_task(task_id, user_id)
        if not task:
            return None
            
        # Upload to storage
        file_url = await self.file_storage.upload(file_content, filename, content_type)
        
        attachment = Attachment(
            task_id=task_id,
            filename=filename,
            file_url=file_url,
            file_size_bytes=len(file_content),
            content_type=content_type
        )
        
        await self.task_repo.add_attachment(attachment)
        
        # Return updated task
        return await self.task_repo.get_by_id(task_id)

    async def remove_attachment(self, user_id: UUID, attachment_id: UUID) -> bool:
        attachment = await self.task_repo.get_attachment_by_id(attachment_id)
        if not attachment:
            return False
            
        task = await self.get_task(attachment.task_id, user_id)
        if not task:
            return False
            
        # Remove from storage
        await self.file_storage.delete(attachment.file_url)
        
        return await self.task_repo.delete_attachment(attachment_id)
