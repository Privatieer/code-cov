from typing import List, Optional
from uuid import UUID
from backend.src.domain.entities.models import TaskList
from backend.src.domain.ports.repositories.base import ITaskListRepository
from backend.src.application.dtos.task_list_dtos import TaskListCreateDTO, TaskListUpdateDTO

class TaskListUseCase:
    def __init__(self, task_list_repo: ITaskListRepository):
        self.task_list_repo = task_list_repo

    async def create_task_list(self, user_id: UUID, dto: TaskListCreateDTO) -> TaskList:
        task_list = TaskList(
            user_id=user_id,
            name=dto.name
        )
        return await self.task_list_repo.create(task_list)

    async def get_user_task_lists(self, user_id: UUID) -> List[TaskList]:
        return await self.task_list_repo.list_by_user(user_id)

    async def get_task_list(self, task_list_id: UUID, user_id: UUID) -> Optional[TaskList]:
        task_list = await self.task_list_repo.get_by_id(task_list_id)
        if task_list and task_list.user_id == user_id:
            return task_list
        return None

    async def update_task_list(self, task_list_id: UUID, user_id: UUID, dto: TaskListUpdateDTO) -> Optional[TaskList]:
        task_list = await self.get_task_list(task_list_id, user_id)
        if not task_list:
            return None
        
        if dto.name is not None:
            task_list.name = dto.name
            
        return await self.task_list_repo.update(task_list)

    async def delete_task_list(self, task_list_id: UUID, user_id: UUID) -> bool:
        task_list = await self.get_task_list(task_list_id, user_id)
        if not task_list:
            return False
        return await self.task_list_repo.delete(task_list_id)

