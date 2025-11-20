from enum import Enum
from typing import Optional, List
from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr, ConfigDict

def utc_now():
    return datetime.now(timezone.utc)

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(BaseModel):
    """
    User Domain Entity.
    Represents a registered user in the system.
    """
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    password_hash: str
    role: UserRole = Field(default=UserRole.USER)
    is_verified: bool = Field(default=False)
    verification_token: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    model_config = ConfigDict(from_attributes=True)

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Attachment(BaseModel):
    """
    Attachment Domain Entity.
    Represents a file attached to a task.
    """
    id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    filename: str
    file_url: str
    file_size_bytes: int
    content_type: str
    created_at: datetime = Field(default_factory=utc_now)

    model_config = ConfigDict(from_attributes=True)

class TaskList(BaseModel):
    """
    TaskList Domain Entity.
    Represents a grouping of tasks (e.g., 'Work', 'Personal').
    """
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    name: str = Field(min_length=1, max_length=100)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    model_config = ConfigDict(from_attributes=True)

class ChecklistItem(BaseModel):
    """
    ChecklistItem Domain Entity.
    A single item within a checklist.
    """
    id: UUID = Field(default_factory=uuid4)
    checklist_id: UUID
    content: str = Field(min_length=1, max_length=500)
    is_completed: bool = Field(default=False)
    position: int = Field(default=0)
    created_at: datetime = Field(default_factory=utc_now)
    
    model_config = ConfigDict(from_attributes=True)

class Checklist(BaseModel):
    """
    Checklist Domain Entity.
    A list of to-do items within a task.
    """
    id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    title: str = Field(min_length=1, max_length=100)
    items: List[ChecklistItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    model_config = ConfigDict(from_attributes=True)

class Task(BaseModel):
    """
    Task Domain Entity. 
    The core organizational unit. Can contain attachments and checklists.
    """
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    task_list_id: Optional[UUID] = None
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)

    # Aggregate relationships
    attachments: list[Attachment] = Field(default_factory=list)
    checklists: list[Checklist] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    model_config = ConfigDict(from_attributes=True)

    def is_overdue(self) -> bool:
        """Checks if the task is past its due date and not completed."""
        if not self.due_date:
            return False
        return utc_now() > self.due_date and self.status != TaskStatus.DONE

