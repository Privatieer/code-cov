from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query, Request, Response
from typing import Any, List, Optional
from uuid import UUID
from sqlalchemy.exc import IntegrityError

from backend.src.application.use_cases.task_use_case import TaskUseCase
from backend.src.application.dtos.task_dtos import TaskCreateDTO, TaskUpdateDTO, TaskResponseDTO
from backend.src.interface.api.dependencies import get_task_use_case, get_current_user_id
from backend.src.domain.entities.models import TaskPriority, TaskStatus
from backend.src.infrastructure.middleware.rate_limiter import conditional_limit

router = APIRouter()

@router.post("/", response_model=TaskResponseDTO, status_code=status.HTTP_201_CREATED)
@conditional_limit("60/minute")
async def create_task(
    request: Request,
    task_dto: TaskCreateDTO,
    user_id: str = Depends(get_current_user_id),
    task_uc: TaskUseCase = Depends(get_task_use_case),
):
    try:
        task = await task_uc.create_task(UUID(user_id), task_dto)
        # Explicitly convert to DTO to ensure proper serialization
        return TaskResponseDTO.model_validate(task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        # Check if it's a foreign key violation for user_id
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if 'user_id_fkey' in error_msg or 'users' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account not found. Please log in again."
            )
        raise HTTPException(status_code=400, detail=f"Database error: {error_msg}")

@router.get("/", response_model=List[TaskResponseDTO])
async def list_tasks(
    user_id: str = Depends(get_current_user_id),
    task_uc: TaskUseCase = Depends(get_task_use_case),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    task_list_id: Optional[UUID] = Query(None),
    limit: int = 20,
    offset: int = 0,
):
    filters = {
        "status": status, 
        "priority": priority, 
        "task_list_id": task_list_id,
        "search": search
    }
    tasks = await task_uc.get_user_tasks(UUID(user_id), filters, limit, offset)
    return [TaskResponseDTO.model_validate(task) for task in tasks]

@router.get("/{task_id}", response_model=TaskResponseDTO)
async def get_task(
    task_id: UUID,
    user_id: str = Depends(get_current_user_id),
    task_uc: TaskUseCase = Depends(get_task_use_case)
) -> Any:
    task = await task_uc.get_task(task_id, UUID(user_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponseDTO.model_validate(task)

@router.put("/{task_id}", response_model=TaskResponseDTO)
async def update_task(
    task_id: UUID,
    task_in: TaskUpdateDTO,
    user_id: str = Depends(get_current_user_id),
    task_uc: TaskUseCase = Depends(get_task_use_case)
) -> Any:
    try:
        task = await task_uc.update_task(task_id, UUID(user_id), task_in)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskResponseDTO.model_validate(task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    user_id: str = Depends(get_current_user_id),
    task_uc: TaskUseCase = Depends(get_task_use_case)
) -> Any:
    success = await task_uc.delete_task(task_id, UUID(user_id))
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}

@router.post("/{task_id}/attachments", response_model=TaskResponseDTO)
async def upload_attachment(
    task_id: UUID,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    task_uc: TaskUseCase = Depends(get_task_use_case)
) -> Any:
    content = await file.read()
    task = await task_uc.add_attachment(
        task_id, 
        UUID(user_id), 
        content, 
        file.filename, 
        file.content_type
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponseDTO.model_validate(task)

@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_attachment(
    attachment_id: UUID,
    user_id: str = Depends(get_current_user_id),
    task_uc: TaskUseCase = Depends(get_task_use_case),
):
    success = await task_uc.remove_attachment(UUID(user_id), attachment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found or user does not have permission",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
