"""
Pytest configuration and shared fixtures
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from backend.src.domain.entities.models import Task, User, Checklist, ChecklistItem, TaskStatus, TaskPriority
from backend.src.domain.ports.repositories.base import ITaskRepository, IUserRepository, IChecklistRepository, IFileStorage
from backend.src.infrastructure.persistence.sqlalchemy.database import Base
from backend.src.infrastructure.persistence.sqlalchemy.models.schema import (
    UserModel, TaskModel, ChecklistModel, ChecklistItemModel
)


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
def mock_user_id() -> UUID:
    """Generate a test user ID"""
    return uuid4()


@pytest.fixture
def mock_task_id() -> UUID:
    """Generate a test task ID"""
    return uuid4()


@pytest.fixture
def mock_checklist_id() -> UUID:
    """Generate a test checklist ID"""
    return uuid4()


@pytest.fixture
def sample_user(mock_user_id: UUID) -> User:
    """Create a sample user"""
    return User(
        id=mock_user_id,
        email="test@example.com",
        password_hash="hashed_password",
        role="user",
        is_verified=True
    )


@pytest.fixture
def sample_task(mock_user_id: UUID, mock_task_id: UUID) -> Task:
    """Create a sample task"""
    return Task(
        id=mock_task_id,
        user_id=mock_user_id,
        title="Test Task",
        description="Test Description",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        tags=["test"]
    )


@pytest.fixture
def sample_checklist(mock_task_id: UUID, mock_checklist_id: UUID) -> Checklist:
    """Create a sample checklist"""
    return Checklist(
        id=mock_checklist_id,
        task_id=mock_task_id,
        title="Test Checklist"
    )


@pytest.fixture
def mock_task_repository() -> ITaskRepository:
    """Create a mock task repository"""
    repo = AsyncMock(spec=ITaskRepository)
    return repo


@pytest.fixture
def mock_user_repository() -> IUserRepository:
    """Create a mock user repository"""
    repo = AsyncMock(spec=IUserRepository)
    return repo


@pytest.fixture
def mock_checklist_repository() -> IChecklistRepository:
    """Create a mock checklist repository"""
    repo = AsyncMock(spec=IChecklistRepository)
    return repo


@pytest.fixture
def mock_file_storage() -> IFileStorage:
    """Create a mock file storage"""
    storage = AsyncMock(spec=IFileStorage)
    storage.upload = AsyncMock(return_value="https://example.com/file.pdf")
    storage.delete = AsyncMock(return_value=True)
    return storage

