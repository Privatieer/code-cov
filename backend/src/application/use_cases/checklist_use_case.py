from typing import Optional
from uuid import UUID
from backend.src.domain.entities.models import Checklist, ChecklistItem, Task
from backend.src.domain.ports.repositories.base import IChecklistRepository, ITaskRepository
from backend.src.application.dtos.task_dtos import ChecklistCreateDTO, ChecklistItemCreateDTO, ChecklistItemUpdateDTO

class ChecklistUseCase:
    def __init__(self, checklist_repo: IChecklistRepository, task_repo: ITaskRepository):
        self.checklist_repo = checklist_repo
        self.task_repo = task_repo

    async def create_checklist(self, task_id: UUID, user_id: UUID, dto: ChecklistCreateDTO) -> Optional[Checklist]:
        task = await self.task_repo.get_by_id(task_id)
        if not task or task.user_id != user_id:
            return None
            
        checklist = Checklist(
            task_id=task_id,
            title=dto.title
        )
        return await self.checklist_repo.create_checklist(checklist)

    async def delete_checklist(self, checklist_id: UUID, user_id: UUID) -> bool:
        checklist = await self.checklist_repo.get_checklist_by_id(checklist_id)
        if not checklist:
            return False
            
        task = await self.task_repo.get_by_id(checklist.task_id)
        if not task or task.user_id != user_id:
            return False
            
        return await self.checklist_repo.delete_checklist(checklist_id)

    async def add_item(self, checklist_id: UUID, user_id: UUID, dto: ChecklistItemCreateDTO) -> Optional[ChecklistItem]:
        checklist = await self.checklist_repo.get_checklist_by_id(checklist_id)
        if not checklist:
            return None
            
        task = await self.task_repo.get_by_id(checklist.task_id)
        if not task or task.user_id != user_id:
            return None
            
        item = ChecklistItem(
            checklist_id=checklist_id,
            content=dto.content,
            position=dto.position
        )
        return await self.checklist_repo.add_item(item)

    async def update_item(self, item_id: UUID, user_id: UUID, dto: ChecklistItemUpdateDTO) -> Optional[ChecklistItem]:
        item = await self.checklist_repo.get_item_by_id(item_id)
        if not item:
            return None
            
        checklist = await self.checklist_repo.get_checklist_by_id(item.checklist_id)
        task = await self.task_repo.get_by_id(checklist.task_id)
        if not task or task.user_id != user_id:
            return None
            
        if dto.content is not None:
            item.content = dto.content
        if dto.is_completed is not None:
            item.is_completed = dto.is_completed
        if dto.position is not None:
            item.position = dto.position
            
        return await self.checklist_repo.update_item(item)

    async def delete_item(self, item_id: UUID, user_id: UUID) -> bool:
        item = await self.checklist_repo.get_item_by_id(item_id)
        if not item:
            return False
            
        checklist = await self.checklist_repo.get_checklist_by_id(item.checklist_id)
        task = await self.task_repo.get_by_id(checklist.task_id)
        if not task or task.user_id != user_id:
            return False
            
        return await self.checklist_repo.delete_item(item_id)
    
    async def get_checklist(self, checklist_id: UUID, user_id: UUID) -> Optional[Checklist]:
        checklist = await self.checklist_repo.get_checklist_by_id(checklist_id)
        if not checklist:
            return None
            
        task = await self.task_repo.get_by_id(checklist.task_id)
        if not task or task.user_id != user_id:
            return None
            
        return checklist

