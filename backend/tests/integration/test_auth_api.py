"""
Integration tests for Auth API endpoints (User registration and deletion)
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4
from backend.src.infrastructure.persistence.sqlalchemy.models.schema import UserModel
from backend.src.infrastructure.security.hashing import get_password_hash


@pytest.mark.integration
class TestUserRegistrationAPI:
    """Integration tests for user registration"""
    
    @pytest.mark.asyncio
    async def test_register_user_success(
        self,
        client: AsyncClient
    ):
        """Test successful user registration"""
        # Arrange
        user_data = {
            "email": f"newuser_{uuid4().hex[:8]}@example.com",
            "password": "SecurePassword123!"
        }
        
        # Act
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == user_data["email"]
        assert data["role"] == "user"
        assert "password" not in data  # Password should never be in response
    
    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(
        self,
        client: AsyncClient,
        test_user: UserModel
    ):
        """Test registration fails with duplicate email"""
        # Arrange
        user_data = {
            "email": test_user.email,  # Use existing user's email
            "password": "AnotherPassword123!"
        }
        
        # Act
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_user_invalid_email(
        self,
        client: AsyncClient
    ):
        """Test registration fails with invalid email format"""
        # Arrange
        user_data = {
            "email": "not-an-email",
            "password": "SecurePassword123!"
        }
        
        # Act
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_register_user_weak_password(
        self,
        client: AsyncClient
    ):
        """Test registration fails with weak password"""
        test_cases = [
            ("123", "too short"),
            ("password", "no uppercase or digit"),
            ("PASSWORD", "no lowercase or digit"),
            ("Password", "no digit"),
            ("Password1", "valid password"),  # This should work
        ]
        
        for password, description in test_cases:
            user_data = {
                "email": f"user_{uuid4().hex[:8]}@example.com",
                "password": password
            }
            
            response = await client.post("/api/v1/auth/register", json=user_data)
            
            if description == "valid password":
                assert response.status_code == 200, f"Valid password '{password}' should succeed"
            else:
                assert response.status_code == 422, f"Weak password '{password}' ({description}) should fail"
                data = response.json()
                assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_register_user_missing_fields(
        self,
        client: AsyncClient
    ):
        """Test registration fails with missing required fields"""
        # Test missing email
        response = await client.post("/api/v1/auth/register", json={"password": "Password123!"})
        assert response.status_code == 422
        
        # Test missing password
        response = await client.post("/api/v1/auth/register", json={"email": "test@example.com"})
        assert response.status_code == 422
        
        # Test empty body
        response = await client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422


@pytest.mark.integration
class TestUserDeletionAPI:
    """Integration tests for user deletion"""
    
    @pytest.mark.asyncio
    async def test_delete_user_success_own_account(
        self,
        authenticated_client: AsyncClient,
        test_user: UserModel,
        test_db_session
    ):
        """Test user can delete their own account"""
        # Act
        response = await authenticated_client.delete(f"/api/v1/auth/users/{test_user.id}")
        
        # Assert
        assert response.status_code == 204
        
        # Verify user is actually deleted from database
        from sqlalchemy import select
        from backend.src.infrastructure.persistence.sqlalchemy.models.schema import UserModel
        query = select(UserModel).where(UserModel.id == test_user.id)
        result = await test_db_session.execute(query)
        deleted_user = result.scalar_one_or_none()
        assert deleted_user is None
    
    @pytest.mark.asyncio
    async def test_delete_user_forbidden_other_user(
        self,
        authenticated_client: AsyncClient,
        test_db_session
    ):
        """Test user cannot delete another user's account"""
        # Arrange - create another user
        other_user_id = uuid4()
        other_user = UserModel(
            id=other_user_id,
            email=f"other_{uuid4().hex[:8]}@example.com",
            password_hash=get_password_hash("password123"),
            role="user",
            is_verified=True
        )
        test_db_session.add(other_user)
        await test_db_session.commit()
        
        # Act - try to delete other user's account
        response = await authenticated_client.delete(f"/api/v1/auth/users/{other_user_id}")
        
        # Assert
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "own account" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(
        self,
        authenticated_client: AsyncClient
    ):
        """Test deleting non-existent user returns 404"""
        # Arrange
        fake_user_id = uuid4()
        
        # Act
        response = await authenticated_client.delete(f"/api/v1/auth/users/{fake_user_id}")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_delete_user_unauthorized(
        self,
        client: AsyncClient,
        test_user: UserModel
    ):
        """Test deleting user without authentication returns 401"""
        # Act
        response = await client.delete(f"/api/v1/auth/users/{test_user.id}")
        
        # Assert
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_delete_user_admin_can_delete_any_user(
        self,
        test_db_session,
        override_get_db
    ):
        """Test admin can delete any user account"""
        from httpx import AsyncClient
        from backend.src.interface.main import app
        from backend.src.infrastructure.security.jwt_token import create_access_token
        
        # Arrange - create admin user
        admin_id = uuid4()
        admin_user = UserModel(
            id=admin_id,
            email=f"admin_{uuid4().hex[:8]}@example.com",
            password_hash=get_password_hash("adminpass123"),
            role="admin",
            is_verified=True
        )
        test_db_session.add(admin_user)
        
        # Create regular user to delete
        target_user_id = uuid4()
        target_user = UserModel(
            id=target_user_id,
            email=f"target_{uuid4().hex[:8]}@example.com",
            password_hash=get_password_hash("targetpass123"),
            role="user",
            is_verified=True
        )
        test_db_session.add(target_user)
        await test_db_session.commit()
        
        # Create authenticated client for admin
        admin_token = create_access_token({"sub": str(admin_id)})
        async with AsyncClient(app=app, base_url="http://test") as admin_client:
            admin_client.headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Act
            response = await admin_client.delete(f"/api/v1/auth/users/{target_user_id}")
            
            # Assert
            assert response.status_code == 204
            
            # Verify target user is deleted
            from sqlalchemy import select
            query = select(UserModel).where(UserModel.id == target_user_id)
            result = await test_db_session.execute(query)
            deleted_user = result.scalar_one_or_none()
            assert deleted_user is None
    
    @pytest.mark.asyncio
    async def test_delete_user_cascades_to_tasks(
        self,
        authenticated_client: AsyncClient,
        test_user: UserModel,
        test_db_session
    ):
        """Test that deleting a user also deletes their tasks (cascade)"""
        from backend.src.infrastructure.persistence.sqlalchemy.models.schema import TaskModel
        
        # Arrange - create a task for the user
        task = TaskModel(
            id=uuid4(),
            user_id=test_user.id,
            title="Test Task",
            status="todo",
            priority="medium"
        )
        test_db_session.add(task)
        await test_db_session.commit()
        task_id = task.id
        
        # Act - delete user
        response = await authenticated_client.delete(f"/api/v1/auth/users/{test_user.id}")
        assert response.status_code == 204
        
        # Assert - task should be deleted (cascade)
        from sqlalchemy import select
        query = select(TaskModel).where(TaskModel.id == task_id)
        result = await test_db_session.execute(query)
        deleted_task = result.scalar_one_or_none()
        assert deleted_task is None

