from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from backend.src.domain.entities.models import Attachment, User, Task, TaskList, Checklist, ChecklistItem

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_verification_token(self, token: str) -> Optional[User]:
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        pass

class ITaskListRepository(ABC):
    @abstractmethod
    async def get_by_id(self, task_list_id: UUID) -> Optional[TaskList]:
        pass

    @abstractmethod
    async def create(self, task_list: TaskList) -> TaskList:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> List[TaskList]:
        pass

    @abstractmethod
    async def update(self, task_list: TaskList) -> TaskList:
        pass

    @abstractmethod
    async def delete(self, task_list_id: UUID) -> bool:
        pass

class IChecklistRepository(ABC):
    @abstractmethod
    async def create_checklist(self, checklist: Checklist) -> Checklist:
        pass
    
    @abstractmethod
    async def get_checklist_by_id(self, checklist_id: UUID) -> Optional[Checklist]:
        pass
    
    @abstractmethod
    async def delete_checklist(self, checklist_id: UUID) -> bool:
        pass
    
    @abstractmethod
    async def add_item(self, item: ChecklistItem) -> ChecklistItem:
        pass
    
    @abstractmethod
    async def update_item(self, item: ChecklistItem) -> ChecklistItem:
        pass
    
    @abstractmethod
    async def delete_item(self, item_id: UUID) -> bool:
        pass
    
    @abstractmethod
    async def get_item_by_id(self, item_id: UUID) -> Optional[ChecklistItem]:
        pass

class ITaskRepository(ABC):
    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        pass

    @abstractmethod
    async def create(self, task: Task) -> Task:
        pass

    @abstractmethod
    async def list_by_user(
        self, 
        user_id: UUID,
        filters: dict = None, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Task]:
        pass

    @abstractmethod
    async def update(self, task: Task) -> Task:
        pass

    @abstractmethod
    async def delete(self, task_id: UUID) -> bool:
        pass
        
    @abstractmethod
    async def add_attachment(self, attachment: Attachment) -> Attachment:
        """Adds an attachment record to the database."""
        pass

    @abstractmethod
    async def get_attachment_by_id(self, attachment_id: UUID) -> Optional[Attachment]:
        """Gets a single attachment by its ID."""
        pass

    @abstractmethod
    async def delete_attachment(self, attachment_id: UUID) -> bool:
        """Deletes an attachment record from the database."""
        pass

    @abstractmethod
    async def get_due_soon(self, hours: int = 24) -> List[Task]:
        """Get tasks due within the next N hours that are not done."""
        pass

class IFileStorage(ABC):
    @abstractmethod
    async def upload(self, file_content: bytes, filename: str, content_type: str) -> str:
        """Uploads file and returns the URL/key"""
        pass

    @abstractmethod
    async def delete(self, file_url: str) -> bool:
        pass
