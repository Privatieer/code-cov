"""
E2E test fixtures and configuration
"""
import pytest
import os

# Try to import playwright, skip E2E tests if not available
try:
    from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    # Create dummy types for type checking
    Page = None
    Browser = None
    BrowserContext = None
    sync_playwright = None

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import event

from backend.src.infrastructure.persistence.sqlalchemy.database import Base
from backend.src.interface.api.dependencies import get_db_session
from backend.src.interface.main import app
from backend.src.infrastructure.persistence.sqlalchemy.models.schema import UserModel
from backend.src.infrastructure.security.hashing import get_password_hash
from uuid import uuid4

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8004")


@pytest.fixture(scope="session")
def browser():
    """Create a browser instance for E2E tests"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed. Install with: poetry add --group dev playwright && poetry run playwright install chromium")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser: Browser):
    """Create a new page for each test"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed")
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True
    )
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="function")
async def test_db_session():
    """Create a test database session for E2E tests"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(sync_conn, checkfirst=True))
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn))
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def override_get_db(test_db_session):
    """Override the get_db dependency"""
    async def _get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db_session] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def api_client(override_get_db) -> AsyncClient:
    """Create an API client for E2E tests"""
    async with AsyncClient(app=app, base_url=BACKEND_URL) as ac:
        yield ac


@pytest.fixture(scope="function")
async def test_user(test_db_session: AsyncSession):
    """Create a test user for E2E tests"""
    user_id = uuid4()
    user = UserModel(
        id=user_id,
        email="e2e-test@example.com",
        password_hash=get_password_hash("TestPassword123!"),
        role="user",
        is_verified=True
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    return user

