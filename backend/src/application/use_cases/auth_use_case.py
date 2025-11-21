from backend.src.domain.entities.models import User, UserRole
from backend.src.domain.ports.repositories.base import IUserRepository
from backend.src.infrastructure.security.hashing import get_password_hash, verify_password
from backend.src.infrastructure.security.jwt_token import create_access_token
from backend.src.application.dtos.auth_dtos import UserCreateDTO, UserLoginDTO, TokenDTO
from backend.src.config import settings
from typing import Optional
from uuid import UUID
import uuid
import structlog

logger = structlog.get_logger()

class AuthUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def register_user(self, dto: UserCreateDTO) -> User:
        existing_user = await self.user_repo.get_by_email(dto.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        hashed_password = get_password_hash(dto.password)
        verification_token = str(uuid.uuid4())
        
        new_user = User(
            email=dto.email,
            password_hash=hashed_password,
            verification_token=verification_token,
            is_verified=settings.TESTING  # Auto-verify in testing mode
        )
        
        user = await self.user_repo.create(new_user)
        
        # In a real app, we would send an email here.
        logger.info("Verification Email Sent", email=user.email, token=verification_token)
        
        return user

    async def verify_user(self, token: str) -> bool:
        user = await self.user_repo.get_by_verification_token(token)
        if not user:
            return False
            
        if user.is_verified:
            return True
            
        user.is_verified = True
        user.verification_token = None # Invalidate token
        await self.user_repo.update(user)
        return True

    async def authenticate_user(self, dto: UserLoginDTO) -> Optional[TokenDTO]:
        user = await self.user_repo.get_by_email(dto.email)
        if not user:
            logger.warning("Login attempt with non-existent email", email=dto.email)
            return None
        
        if not verify_password(dto.password, user.password_hash):
            logger.warning("Login attempt with incorrect password", email=dto.email)
            return None
        
        # Allow login even if not verified for admin users, or require verification for regular users
        if not user.is_verified and user.role != UserRole.ADMIN:
            logger.warning("Login attempt with unverified account", email=dto.email)
            return None
            
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        logger.info("User authenticated successfully", email=user.email, role=user.role.value)
        return TokenDTO(access_token=access_token, token_type="bearer")
    
    async def delete_user(self, user_id: UUID, requesting_user_id: UUID) -> bool:
        """
        Delete a user account.
        Users can only delete their own account unless they are admin.
        """
        requesting_user = await self.user_repo.get_by_id(requesting_user_id)
        if not requesting_user:
            raise ValueError("Requesting user not found")
        
        target_user = await self.user_repo.get_by_id(user_id)
        if not target_user:
            return False
        
        # Users can only delete their own account, unless they are admin
        if requesting_user.role != UserRole.ADMIN and requesting_user.id != user_id:
            raise ValueError("You can only delete your own account")
        
        success = await self.user_repo.delete(user_id)
        if success:
            logger.info("User deleted", user_id=str(user_id), deleted_by=str(requesting_user_id))
        return success