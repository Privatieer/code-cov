from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from typing import Any, List
from uuid import UUID
from backend.src.infrastructure.middleware.rate_limiter import conditional_limit

from backend.src.application.use_cases.task_list_use_case import TaskListUseCase
from backend.src.application.dtos.task_list_dtos import TaskListCreateDTO, TaskListUpdateDTO, TaskListResponseDTO
from backend.src.interface.api.dependencies import get_task_list_use_case, get_current_user_id

router = APIRouter()

@router.post("/", response_model=TaskListResponseDTO, status_code=status.HTTP_201_CREATED)
@conditional_limit("60/minute")
async def create_task_list(
    request: Request,
    dto: TaskListCreateDTO,
    user_id: str = Depends(get_current_user_id),
    uc: TaskListUseCase = Depends(get_task_list_use_case),
):
    return await uc.create_task_list(UUID(user_id), dto)

@router.get("/", response_model=List[TaskListResponseDTO])
async def list_task_lists(
    user_id: str = Depends(get_current_user_id),
    uc: TaskListUseCase = Depends(get_task_list_use_case),
):
    return await uc.get_user_task_lists(UUID(user_id))

@router.get("/{task_list_id}", response_model=TaskListResponseDTO)
async def get_task_list(
    task_list_id: UUID,
    user_id: str = Depends(get_current_user_id),
    uc: TaskListUseCase = Depends(get_task_list_use_case),
):
    task_list = await uc.get_task_list(task_list_id, UUID(user_id))
    if not task_list:
        raise HTTPException(status_code=404, detail="Task List not found")
    return task_list

@router.put("/{task_list_id}", response_model=TaskListResponseDTO)
async def update_task_list(
    task_list_id: UUID,
    dto: TaskListUpdateDTO,
    user_id: str = Depends(get_current_user_id),
    uc: TaskListUseCase = Depends(get_task_list_use_case),
):
    task_list = await uc.update_task_list(task_list_id, UUID(user_id), dto)
    if not task_list:
        raise HTTPException(status_code=404, detail="Task List not found")
    return task_list

@router.delete("/{task_list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_list(
    task_list_id: UUID,
    user_id: str = Depends(get_current_user_id),
    uc: TaskListUseCase = Depends(get_task_list_use_case),
):
    success = await uc.delete_task_list(task_list_id, UUID(user_id))
    if not success:
        raise HTTPException(status_code=404, detail="Task List not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

