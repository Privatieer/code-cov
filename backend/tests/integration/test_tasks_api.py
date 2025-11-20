"""
Integration tests for Tasks API endpoints
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timedelta


@pytest.mark.integration
class TestTasksAPI:
    """Integration tests for Tasks API"""
    
    @pytest.mark.asyncio
    async def test_create_task_success(
        self,
        authenticated_client: AsyncClient
    ):
        """Test successful task creation"""
        # Arrange
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "priority": "medium"
        }
        
        # Act
        response = await authenticated_client.post("/api/v1/tasks/", json=task_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["priority"] == "medium"
        assert data["status"] == "todo"
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_task_with_due_date(
        self,
        authenticated_client: AsyncClient
    ):
        """Test task creation with due date"""
        # Arrange
        due_date = (datetime.now() + timedelta(days=1)).isoformat()
        task_data = {
            "title": "Task with Due Date",
            "priority": "high",
            "due_date": due_date
        }
        
        # Act
        response = await authenticated_client.post("/api/v1/tasks/", json=task_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Task with Due Date"
        assert data["priority"] == "high"
    
    @pytest.mark.asyncio
    async def test_create_task_unauthorized(
        self,
        client: AsyncClient
    ):
        """Test task creation without authentication"""
        # Arrange
        task_data = {
            "title": "Test Task",
            "priority": "medium"
        }
        
        # Act
        response = await client.post("/api/v1/tasks/", json=task_data)
        
        # Assert
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_tasks_success(
        self,
        authenticated_client: AsyncClient
    ):
        """Test retrieving user tasks"""
        # Arrange - create a task first
        task_data = {
            "title": "Test Task",
            "priority": "medium"
        }
        create_response = await authenticated_client.post("/api/v1/tasks/", json=task_data)
        assert create_response.status_code == 201
        
        # Act
        response = await authenticated_client.get("/api/v1/tasks/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_get_task_by_id_success(
        self,
        authenticated_client: AsyncClient
    ):
        """Test retrieving a specific task"""
        # Arrange - create a task first
        task_data = {
            "title": "Specific Task",
            "priority": "medium"
        }
        create_response = await authenticated_client.post("/api/v1/tasks/", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        response = await authenticated_client.get(f"/api/v1/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Specific Task"
    
    @pytest.mark.asyncio
    async def test_update_task_success(
        self,
        authenticated_client: AsyncClient
    ):
        """Test updating a task"""
        # Arrange - create a task first
        task_data = {
            "title": "Original Title",
            "priority": "medium"
        }
        create_response = await authenticated_client.post("/api/v1/tasks/", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - update the task
        update_data = {
            "title": "Updated Title",
            "status": "in_progress"
        }
        response = await authenticated_client.put(f"/api/v1/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"
    
    @pytest.mark.asyncio
    async def test_delete_task_success(
        self,
        authenticated_client: AsyncClient
    ):
        """Test deleting a task"""
        # Arrange - create a task first
        task_data = {
            "title": "Task to Delete",
            "priority": "medium"
        }
        create_response = await authenticated_client.post("/api/v1/tasks/", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        response = await authenticated_client.delete(f"/api/v1/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["ok"] is True
        
        # Verify task is deleted
        get_response = await authenticated_client.get(f"/api/v1/tasks/{task_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_filter_tasks_by_status(
        self,
        authenticated_client: AsyncClient
    ):
        """Test filtering tasks by status"""
        # Arrange - create tasks with different statuses
        task1_data = {"title": "Todo Task", "priority": "medium"}
        task2_data = {"title": "In Progress Task", "priority": "medium"}
        
        create1 = await authenticated_client.post("/api/v1/tasks/", json=task1_data)
        task1_id = create1.json()["id"]
        
        create2 = await authenticated_client.post("/api/v1/tasks/", json=task2_data)
        task2_id = create2.json()["id"]
        
        # Update task2 to in_progress
        await authenticated_client.put(f"/api/v1/tasks/{task2_id}", json={"status": "in_progress"})
        
        # Act - filter by status
        response = await authenticated_client.get("/api/v1/tasks/?status=in_progress")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert all(task["status"] == "in_progress" for task in data)
    
    @pytest.mark.asyncio
    async def test_filter_tasks_by_priority(
        self,
        authenticated_client: AsyncClient
    ):
        """Test filtering tasks by priority"""
        # Arrange - create tasks with different priorities
        task_data = {"title": "High Priority Task", "priority": "high"}
        await authenticated_client.post("/api/v1/tasks/", json=task_data)
        
        # Act - filter by priority
        response = await authenticated_client.get("/api/v1/tasks/?priority=high")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert all(task["priority"] == "high" for task in data)

