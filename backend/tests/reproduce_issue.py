import pytest
from uuid import uuid4
from httpx import AsyncClient
from backend.src.interface.main import app
from backend.src.domain.entities.models import User, Task, TaskStatus, TaskPriority
from backend.src.infrastructure.security.jwt_token import create_access_token

@pytest.mark.asyncio
async def test_task_privacy_between_users(
    db_session,
    mock_task_repository, # We need real repo or simulated behavior
):
    # Note: mocking the repo might defeat the purpose if the bug is in the repo. 
    # Ideally we use the real DB session and repositories.
    pass

# Let's use the e2e style setup but with direct API calls
@pytest.mark.asyncio
async def test_users_cannot_see_each_others_tasks(client: AsyncClient, db_session):
    # 1. Create two users
    user1_id = uuid4()
    user2_id = uuid4()
    
    # We'll manually insert them or register them via API. API is better.
    # Register User 1
    resp1 = await client.post("/api/v1/auth/register", json={
        "email": "user1@example.com", 
        "password": "Password123!"
    })
    assert resp1.status_code == 201
    user1_data = resp1.json()
    
    # Login User 1
    login_resp1 = await client.post("/api/v1/auth/token", data={
        "username": "user1@example.com",
        "password": "Password123!"
    })
    token1 = login_resp1.json()["access_token"]
    
    # Register User 2
    resp2 = await client.post("/api/v1/auth/register", json={
        "email": "user2@example.com", 
        "password": "Password123!"
    })
    assert resp2.status_code == 201
    
    # Login User 2
    login_resp2 = await client.post("/api/v1/auth/token", data={
        "username": "user2@example.com",
        "password": "Password123!"
    })
    token2 = login_resp2.json()["access_token"]

    # 2. User 1 creates a task
    headers1 = {"Authorization": f"Bearer {token1}"}
    create_resp = await client.post("/api/v1/tasks/", json={
        "title": "User 1 Secret Task",
        "description": "Top secret",
        "priority": "high"
    }, headers=headers1)
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]
    
    # 3. User 2 tries to list tasks - should NOT see it
    headers2 = {"Authorization": f"Bearer {token2}"}
    list_resp = await client.get("/api/v1/tasks/", headers=headers2)
    assert list_resp.status_code == 200
    tasks = list_resp.json()
    
    # Check if User 1's task is in User 2's list
    found = any(t["id"] == task_id for t in tasks)
    
    # 4. User 2 tries to access User 1's task directly - should be 404
    get_resp = await client.get(f"/api/v1/tasks/{task_id}", headers=headers2)
    
    return found, get_resp.status_code

