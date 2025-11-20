from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any
from uuid import UUID

from backend.src.application.use_cases.auth_use_case import AuthUseCase
from backend.src.application.dtos.auth_dtos import UserCreateDTO, UserLoginDTO, TokenDTO, UserResponseDTO
from backend.src.interface.api.dependencies import get_auth_use_case, get_current_user_id
from backend.src.infrastructure.middleware.rate_limiter import conditional_limit

router = APIRouter()

@router.post("/register", response_model=UserResponseDTO)
@conditional_limit("5/minute")
async def register(
    request: Request,
    user_in: UserCreateDTO,
    auth_uc: AuthUseCase = Depends(get_auth_use_case)
) -> Any:
    try:
        user = await auth_uc.register_user(user_in)
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            role=user.role.value
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/verify")
async def verify_email(
    token: str,
    auth_uc: AuthUseCase = Depends(get_auth_use_case)
) -> Any:
    success = await auth_uc.verify_user(token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    return {"message": "Email verified successfully"}

@router.post("/token", response_model=TokenDTO)
@conditional_limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_uc: AuthUseCase = Depends(get_auth_use_case)
) -> Any:
    dto = UserLoginDTO(email=form_data.username, password=form_data.password)
    token = await auth_uc.authenticate_user(dto)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    requesting_user_id: str = Depends(get_current_user_id),
    auth_uc: AuthUseCase = Depends(get_auth_use_case)
) -> Response:
    """Delete a user account. Users can only delete their own account."""
    try:
        success = await auth_uc.delete_user(user_id, UUID(requesting_user_id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
