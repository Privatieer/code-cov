from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.domain.entities.models import User, UserRole
from backend.src.domain.ports.repositories.base import IUserRepository
from backend.src.infrastructure.persistence.sqlalchemy.models.schema import UserModel

class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: UserModel) -> Optional[User]:
        if not model:
            return None
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            role=UserRole(model.role),
            is_verified=model.is_verified,
            verification_token=model.verification_token,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            password_hash=entity.password_hash,
            role=entity.role.value,
            is_verified=entity.is_verified,
            verification_token=entity.verification_token,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model)

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model)

    async def get_by_verification_token(self, token: str) -> Optional[User]:
        query = select(UserModel).where(UserModel.verification_token == token)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model)

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        self.session.add(model)
        await self.session.commit()
        return await self.get_by_id(user.id)

    async def update(self, user: User) -> User:
        query = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(query)
        existing_model = result.scalar_one_or_none()
        
        if existing_model:
            existing_model.email = user.email
            existing_model.password_hash = user.password_hash
            existing_model.role = user.role.value
            existing_model.is_verified = user.is_verified
            existing_model.verification_token = user.verification_token
            existing_model.updated_at = user.updated_at
            
            await self.session.commit()
            await self.session.refresh(existing_model)
            return await self.get_by_id(user.id)
        return None
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID. Returns True if deleted, False if not found."""
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False

