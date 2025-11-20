"""
Integration test fixtures

Note: Integration tests use SQLite for simplicity, but PostgreSQL-specific features
like ARRAY types are handled via JSON conversion for tags.
"""
import pytest
import warnings
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import event
import json

from backend.src.infrastructure.persistence.sqlalchemy.database import Base, get_db
from backend.src.interface.api.dependencies import get_db_session
from backend.src.interface.main import app
from backend.src.infrastructure.persistence.sqlalchemy.models.schema import (
    UserModel, TaskModel, ChecklistModel, ChecklistItemModel, AttachmentModel, TaskListModel
)
from backend.src.infrastructure.security.hashing import get_password_hash
from uuid import uuid4

# Suppress deprecation warnings from third-party libraries
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="argon2")


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_db_session():
    """Create a test database session"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        # Convert ARRAY columns to TEXT for SQLite compatibility
        cursor.execute("PRAGMA table_info(tasks)")
        cursor.close()
    
    # For SQLite, we'll handle tags as JSON strings
    # Create tables without the ARRAY constraint
    async with engine.begin() as conn:
        # Drop existing tables if any
        await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(sync_conn, checkfirst=True))
        # Create tables - SQLite will store ARRAY as TEXT
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn))
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function", autouse=True)
async def set_test_mode():
    """Set TESTING environment variable to disable rate limiting in tests"""
    import os
    os.environ["TESTING"] = "true"
    yield
    # Clean up - remove TESTING env var after test
    os.environ.pop("TESTING", None)


@pytest.fixture(scope="function")
async def override_get_db(test_db_session):
    """Override the get_db dependency"""
    async def _get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db_session] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(test_db_session: AsyncSession):
    """Create a test user"""
    user_id = uuid4()
    user = UserModel(
        id=user_id,
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="user",
        is_verified=True
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def auth_token(test_user: UserModel, override_get_db):
    """Get authentication token for test user"""
    from backend.src.infrastructure.security.jwt_token import create_access_token
    
    token = create_access_token({"sub": str(test_user.id)})
    return token


@pytest.fixture(scope="function")
async def client(override_get_db) -> AsyncClient:
    """Create a test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def authenticated_client(client: AsyncClient, auth_token: str) -> AsyncClient:
    """Create an authenticated test client"""
    client.headers = {"Authorization": f"Bearer {auth_token}"}
    return client
