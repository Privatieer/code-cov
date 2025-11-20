from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class TaskListCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class TaskListUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class TaskListResponseDTO(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

