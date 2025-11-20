from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional, List, Any, Union
from datetime import datetime
from uuid import UUID
from backend.src.domain.entities.models import TaskStatus, TaskPriority

class AttachmentDTO(BaseModel):
    id: UUID
    filename: str
    file_url: str
    file_size_bytes: int

    model_config = ConfigDict(from_attributes=True)

class ChecklistItemCreateDTO(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)
    position: int = 0

class ChecklistItemUpdateDTO(BaseModel):
    content: Optional[str] = None
    is_completed: Optional[bool] = None
    position: Optional[int] = None

class ChecklistItemResponseDTO(BaseModel):
    id: UUID
    checklist_id: UUID
    content: str
    is_completed: bool
    position: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ChecklistCreateDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)

class ChecklistResponseDTO(BaseModel):
    id: UUID
    task_id: UUID
    title: str
    items: List[ChecklistItemResponseDTO]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TaskCreateDTO(BaseModel):
    task_list_id: Optional[UUID] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    tags: List[str] = []

class TaskUpdateDTO(BaseModel):
    task_list_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None

class TaskResponseDTO(BaseModel):
    id: UUID
    user_id: UUID
    task_list_id: Optional[UUID]
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[datetime]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    attachments: List[AttachmentDTO]
    checklists: List[ChecklistResponseDTO]

    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('status', 'priority', mode='before')
    @classmethod
    def convert_enum_to_string(cls, v: Any) -> str:
        """Convert enum values to strings"""
        if isinstance(v, (TaskStatus, TaskPriority)):
            return v.value
        if isinstance(v, str):
            return v
        # Fallback: try to get value attribute
        if hasattr(v, 'value'):
            return v.value
        return str(v)