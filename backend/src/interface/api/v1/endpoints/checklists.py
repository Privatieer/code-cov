from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from typing import Any, List
from uuid import UUID
from backend.src.infrastructure.middleware.rate_limiter import conditional_limit

from backend.src.application.use_cases.checklist_use_case import ChecklistUseCase
from backend.src.application.dtos.task_dtos import (
    ChecklistCreateDTO, ChecklistResponseDTO, 
    ChecklistItemCreateDTO, ChecklistItemUpdateDTO, ChecklistItemResponseDTO
)
from backend.src.interface.api.dependencies import get_checklist_use_case, get_current_user_id

router = APIRouter()

# Note: Task ID comes from path, but for checklist creation we need it.
# We'll assume the route is mounted under /tasks/{task_id}/checklists or similar
# OR we can have a flat structure. Let's do flat structure for checklists management to avoid deep nesting,
# but creation needs task_id.

# Recommended approach:
# POST /api/v1/tasks/{task_id}/checklists -> Create checklist
# DELETE /api/v1/checklists/{checklist_id} -> Delete checklist
# POST /api/v1/checklists/{checklist_id}/items -> Add item
# PUT /api/v1/checklist-items/{item_id} -> Update item
# DELETE /api/v1/checklist-items/{item_id} -> Delete item

@router.post("/tasks/{task_id}/checklists", response_model=ChecklistResponseDTO, status_code=status.HTTP_201_CREATED)
@conditional_limit("60/minute")
async def create_checklist(
    request: Request,
    task_id: UUID,
    dto: ChecklistCreateDTO,
    user_id: str = Depends(get_current_user_id),
    uc: ChecklistUseCase = Depends(get_checklist_use_case),
):
    checklist = await uc.create_checklist(task_id, UUID(user_id), dto)
    if not checklist:
        raise HTTPException(status_code=404, detail="Task not found or access denied")
    return checklist

@router.get("/checklists/{checklist_id}", response_model=ChecklistResponseDTO)
async def get_checklist(
    checklist_id: UUID,
    user_id: str = Depends(get_current_user_id),
    uc: ChecklistUseCase = Depends(get_checklist_use_case),
):
    checklist = await uc.get_checklist(checklist_id, UUID(user_id))
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found or access denied")
    return checklist

@router.delete("/checklists/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist(
    checklist_id: UUID,
    user_id: str = Depends(get_current_user_id),
    uc: ChecklistUseCase = Depends(get_checklist_use_case),
):
    success = await uc.delete_checklist(checklist_id, UUID(user_id))
    if not success:
        raise HTTPException(status_code=404, detail="Checklist not found or access denied")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/checklists/{checklist_id}/items", response_model=ChecklistItemResponseDTO, status_code=status.HTTP_201_CREATED)
async def add_checklist_item(
    checklist_id: UUID,
    dto: ChecklistItemCreateDTO,
    user_id: str = Depends(get_current_user_id),
    uc: ChecklistUseCase = Depends(get_checklist_use_case),
):
    item = await uc.add_item(checklist_id, UUID(user_id), dto)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist not found or access denied")
    return item

@router.put("/checklist-items/{item_id}", response_model=ChecklistItemResponseDTO)
async def update_checklist_item(
    item_id: UUID,
    dto: ChecklistItemUpdateDTO,
    user_id: str = Depends(get_current_user_id),
    uc: ChecklistUseCase = Depends(get_checklist_use_case),
):
    item = await uc.update_item(item_id, UUID(user_id), dto)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found or access denied")
    return item

@router.delete("/checklist-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist_item(
    item_id: UUID,
    user_id: str = Depends(get_current_user_id),
    uc: ChecklistUseCase = Depends(get_checklist_use_case),
):
    success = await uc.delete_item(item_id, UUID(user_id))
    if not success:
        raise HTTPException(status_code=404, detail="Item not found or access denied")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

