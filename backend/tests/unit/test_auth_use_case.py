"""
Unit tests for AuthUseCase
"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from backend.src.application.use_cases.auth_use_case import AuthUseCase
from backend.src.application.dtos.auth_dtos import UserCreateDTO, UserLoginDTO
from backend.src.domain.entities.models import User, UserRole
from backend.src.domain.ports.repositories.base import IUserRepository


@pytest.mark.unit
class TestAuthUseCase:
    """Test cases for AuthUseCase"""
    
    @pytest.fixture
    def auth_use_case(
        self,
        mock_user_repository: IUserRepository
    ) -> AuthUseCase:
        """Create an AuthUseCase instance with mocked dependencies"""
        return AuthUseCase(mock_user_repository)
    
    @pytest.mark.asyncio
    async def test_register_user_success(
        self,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test successful user registration"""
        # Arrange
        dto = UserCreateDTO(
            email="test@example.com",
            password="Password123"
        )
        
        user_id = uuid4()
        expected_user = User(
            id=user_id,
            email=dto.email,
            password_hash="hashed_password",
            role=UserRole.USER,
            is_verified=False
        )
        
        mock_user_repository.get_by_email = AsyncMock(return_value=None)
        mock_user_repository.create = AsyncMock(return_value=expected_user)
        
        # Act
        result = await auth_use_case.register_user(dto)
        
        # Assert
        assert result == expected_user
        assert result.email == "test@example.com"
        assert result.is_verified is False
        mock_user_repository.get_by_email.assert_called_once_with(dto.email)
        mock_user_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_user_email_exists(
        self,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test user registration fails when email already exists"""
        # Arrange
        dto = UserCreateDTO(
            email="existing@example.com",
            password="Password123"
        )
        
        existing_user = User(
            id=uuid4(),
            email=dto.email,
            password_hash="hashed",
            role=UserRole.USER,
            is_verified=True
        )
        
        mock_user_repository.get_by_email = AsyncMock(return_value=existing_user)
        
        # Act & Assert
        with pytest.raises(ValueError, match="User with this email already exists"):
            await auth_use_case.register_user(dto)
    
    @pytest.mark.asyncio
    @patch('backend.src.application.use_cases.auth_use_case.verify_password')
    async def test_authenticate_user_success(
        self,
        mock_verify_password,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test successful user authentication"""
        # Arrange
        dto = UserLoginDTO(
            email="test@example.com",
            password="password123"
        )
        
        user = User(
            id=uuid4(),
            email=dto.email,
            password_hash="hashed_password",
            role=UserRole.USER,
            is_verified=True
        )
        
        mock_user_repository.get_by_email = AsyncMock(return_value=user)
        mock_verify_password.return_value = True
        
        # Act
        result = await auth_use_case.authenticate_user(dto)
        
        # Assert
        assert result is not None
        assert hasattr(result, 'access_token')
        mock_user_repository.get_by_email.assert_called_once_with(dto.email)
        mock_verify_password.assert_called_once_with(dto.password, user.password_hash)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(
        self,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test authentication fails when user not found"""
        # Arrange
        dto = UserLoginDTO(
            email="nonexistent@example.com",
            password="password123"
        )
        
        mock_user_repository.get_by_email = AsyncMock(return_value=None)
        
        # Act
        result = await auth_use_case.authenticate_user(dto)
        
        # Assert
        assert result is None
        mock_user_repository.get_by_email.assert_called_once_with(dto.email)
    
    @pytest.mark.asyncio
    async def test_verify_user_success(
        self,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test successful user verification"""
        # Arrange
        token = "verification_token_123"
        user_id = uuid4()
        
        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            is_verified=False,
            verification_token=token
        )
        
        mock_user_repository.get_by_verification_token = AsyncMock(return_value=user)
        mock_user_repository.update = AsyncMock(return_value=user)
        
        # Act
        result = await auth_use_case.verify_user(token)
        
        # Assert
        assert result is True
        mock_user_repository.get_by_verification_token.assert_called_once_with(token)
        mock_user_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_verify_user_invalid_token(
        self,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test verification fails with invalid token"""
        # Arrange
        token = "invalid_token"
        mock_user_repository.get_by_verification_token = AsyncMock(return_value=None)
        
        # Act
        result = await auth_use_case.verify_user(token)
        
        # Assert
        assert result is False
        mock_user_repository.get_by_verification_token.assert_called_once_with(token)
    
    @pytest.mark.asyncio
    @patch('backend.src.application.use_cases.auth_use_case.get_password_hash')
    async def test_register_user_password_hashing(
        self,
        mock_hash_password,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test that password is properly hashed during registration"""
        # Arrange
        dto = UserCreateDTO(
            email="newuser@example.com",
            password="SecurePassword123!"
        )
        
        user_id = uuid4()
        expected_user = User(
            id=user_id,
            email=dto.email,
            password_hash="hashed_SecurePassword123!",
            role=UserRole.USER,
            is_verified=False
        )
        
        mock_hash_password.return_value = "hashed_SecurePassword123!"
        mock_user_repository.get_by_email = AsyncMock(return_value=None)
        mock_user_repository.create = AsyncMock(return_value=expected_user)
        
        # Act
        result = await auth_use_case.register_user(dto)
        
        # Assert
        assert result.email == dto.email
        mock_hash_password.assert_called_once_with(dto.password)
        # Verify the created user has the hashed password
        create_call_args = mock_user_repository.create.call_args[0][0]
        assert create_call_args.password_hash == "hashed_SecurePassword123!"
    
    @pytest.mark.asyncio
    async def test_register_user_verification_token_generated(
        self,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test that verification token is generated during registration"""
        # Arrange
        dto = UserCreateDTO(
            email="tokenuser@example.com",
            password="Password123"
        )
        
        user_id = uuid4()
        expected_user = User(
            id=user_id,
            email=dto.email,
            password_hash="hashed",
            role=UserRole.USER,
            is_verified=False,
            verification_token="some_token"
        )
        
        mock_user_repository.get_by_email = AsyncMock(return_value=None)
        mock_user_repository.create = AsyncMock(return_value=expected_user)
        
        # Act
        result = await auth_use_case.register_user(dto)
        
        # Assert
        create_call_args = mock_user_repository.create.call_args[0][0]
        assert create_call_args.verification_token is not None
        assert len(create_call_args.verification_token) > 0
        assert create_call_args.is_verified is False
    
    @pytest.mark.asyncio
    async def test_delete_user_success_own_account(
        self,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test user can delete their own account"""
        # Arrange
        user_id = uuid4()
        requesting_user_id = user_id  # Same user
        
        requesting_user = User(
            id=requesting_user_id,
            email="user@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            is_verified=True
        )
        
        target_user = User(
            id=user_id,
            email="user@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            is_verified=True
        )
        
        mock_user_repository.get_by_id = AsyncMock(side_effect=[requesting_user, target_user])
        mock_user_repository.delete = AsyncMock(return_value=True)
        
        # Act
        result = await auth_use_case.delete_user(user_id, requesting_user_id)
        
        # Assert
        assert result is True
        mock_user_repository.delete.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_delete_user_success_admin(
        self,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test admin can delete any user account"""
        # Arrange
        admin_id = uuid4()
        target_user_id = uuid4()
        
        admin_user = User(
            id=admin_id,
            email="admin@example.com",
            password_hash="hashed",
            role=UserRole.ADMIN,
            is_verified=True
        )
        
        target_user = User(
            id=target_user_id,
            email="target@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            is_verified=True
        )
        
        mock_user_repository.get_by_id = AsyncMock(side_effect=[admin_user, target_user])
        mock_user_repository.delete = AsyncMock(return_value=True)
        
        # Act
        result = await auth_use_case.delete_user(target_user_id, admin_id)
        
        # Assert
        assert result is True
        mock_user_repository.delete.assert_called_once_with(target_user_id)
    
    @pytest.mark.asyncio
    async def test_delete_user_forbidden_other_user(
        self,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test user cannot delete another user's account"""
        # Arrange
        requesting_user_id = uuid4()
        target_user_id = uuid4()
        
        requesting_user = User(
            id=requesting_user_id,
            email="requester@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            is_verified=True
        )
        
        target_user = User(
            id=target_user_id,
            email="target@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            is_verified=True
        )
        
        mock_user_repository.get_by_id = AsyncMock(side_effect=[requesting_user, target_user])
        
        # Act & Assert
        with pytest.raises(ValueError, match="You can only delete your own account"):
            await auth_use_case.delete_user(target_user_id, requesting_user_id)
        
        # Verify delete was not called
        mock_user_repository.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(
        self,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test deleting non-existent user returns False"""
        # Arrange
        requesting_user_id = uuid4()
        target_user_id = uuid4()
        
        requesting_user = User(
            id=requesting_user_id,
            email="requester@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            is_verified=True
        )
        
        mock_user_repository.get_by_id = AsyncMock(side_effect=[requesting_user, None])
        
        # Act
        result = await auth_use_case.delete_user(target_user_id, requesting_user_id)
        
        # Assert
        assert result is False
        mock_user_repository.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_user_requesting_user_not_found(
        self,
        auth_use_case: AuthUseCase,
        mock_user_repository: IUserRepository
    ):
        """Test deleting when requesting user doesn't exist raises error"""
        # Arrange
        requesting_user_id = uuid4()
        target_user_id = uuid4()
        
        mock_user_repository.get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Requesting user not found"):
            await auth_use_case.delete_user(target_user_id, requesting_user_id)

