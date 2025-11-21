import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy import select
from backend.src.infrastructure.persistence.sqlalchemy.models.schema import UserModel

@pytest.mark.integration
@pytest.mark.asyncio
async def test_users_cannot_see_each_others_tasks(client: AsyncClient, test_db_session):
    """
    Reproduction test for privacy issue:
    Ensure User 2 cannot see User 1's tasks.
    """
    # 1. Register User 1
    resp1 = await client.post("/api/v1/auth/register", json={
        "email": "user1@privacy.com", 
        "password": "Password123!"
    })
    assert resp1.status_code in [200, 201], f"User 1 reg failed: {resp1.text}"
    
    # Manually verify User 1
    result = await test_db_session.execute(select(UserModel).where(UserModel.email == "user1@privacy.com"))
    user1 = result.scalar_one()
    user1.is_verified = True
    await test_db_session.commit()
    
    # Login User 1
    login_resp1 = await client.post("/api/v1/auth/token", data={
        "username": "user1@privacy.com",
        "password": "Password123!"
    })
    assert login_resp1.status_code == 200, f"Login 1 failed: {login_resp1.text}"
    token1 = login_resp1.json()["access_token"]
    
    # 2. Register User 2
    resp2 = await client.post("/api/v1/auth/register", json={
        "email": "user2@privacy.com", 
        "password": "Password123!"
    })
    assert resp2.status_code in [200, 201], f"User 2 reg failed: {resp2.text}"
    
    # Manually verify User 2
    result = await test_db_session.execute(select(UserModel).where(UserModel.email == "user2@privacy.com"))
    user2 = result.scalar_one()
    user2.is_verified = True
    await test_db_session.commit()
    
    # Login User 2
    login_resp2 = await client.post("/api/v1/auth/token", data={
        "username": "user2@privacy.com",
        "password": "Password123!"
    })
    assert login_resp2.status_code == 200, f"Login 2 failed: {login_resp2.text}"
    token2 = login_resp2.json()["access_token"]

    # 3. User 1 creates a task
    headers1 = {"Authorization": f"Bearer {token1}"}
    create_resp = await client.post("/api/v1/tasks/", json={
        "title": "User 1 Secret Task",
        "description": "Top secret",
        "priority": "high"
    }, headers=headers1)
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]
    
    # 4. User 2 tries to list tasks - should NOT see it
    headers2 = {"Authorization": f"Bearer {token2}"}
    list_resp = await client.get("/api/v1/tasks/", headers=headers2)
    assert list_resp.status_code == 200
    tasks = list_resp.json()
    
    # Check if User 1's task is in User 2's list
    found = any(t["id"] == task_id for t in tasks)
    
    assert not found, "PRIVACY LEAK: User 2 can see User 1's task in list!"
    
    # 5. User 2 tries to access User 1's task directly - should be 404
    get_resp = await client.get(f"/api/v1/tasks/{task_id}", headers=headers2)
    
    assert get_resp.status_code == 404, f"PRIVACY LEAK: User 2 can access User 1's task directly! Status: {get_resp.status_code}"

