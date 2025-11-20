"""
Integration tests for Checklists API endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestChecklistsAPI:
    """Integration tests for Checklists API"""
    
    @pytest.mark.asyncio
    async def test_create_checklist_success(
        self,
        authenticated_client: AsyncClient
    ):
        """Test successful checklist creation"""
        # Arrange - create a task first
        task_data = {"title": "Test Task", "priority": "medium"}
        task_response = await authenticated_client.post("/api/v1/tasks/", json=task_data)
        task_id = task_response.json()["id"]
        
        checklist_data = {"title": "Test Checklist"}
        
        # Act
        response = await authenticated_client.post(
            f"/api/v1/tasks/{task_id}/checklists",
            json=checklist_data
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Checklist"
        assert data["task_id"] == task_id
        assert "id" in data
        assert data["items"] == []
    
    @pytest.mark.asyncio
    async def test_delete_checklist_success(
        self,
        authenticated_client: AsyncClient
    ):
        """Test successful checklist deletion"""
        # Arrange - create task and checklist
        task_data = {"title": "Test Task", "priority": "medium"}
        task_response = await authenticated_client.post("/api/v1/tasks/", json=task_data)
        task_id = task_response.json()["id"]
        
        checklist_data = {"title": "Checklist to Delete"}
        checklist_response = await authenticated_client.post(
            f"/api/v1/tasks/{task_id}/checklists",
            json=checklist_data
        )
        checklist_id = checklist_response.json()["id"]
        
        # Act
        response = await authenticated_client.delete(f"/api/v1/checklists/{checklist_id}")
        
        # Assert
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_add_checklist_item_success(
        self,
        authenticated_client: AsyncClient
    ):
        """Test successful checklist item addition"""
        # Arrange - create task and checklist
        task_data = {"title": "Test Task", "priority": "medium"}
        task_response = await authenticated_client.post("/api/v1/tasks/", json=task_data)
        task_id = task_response.json()["id"]
        
        checklist_data = {"title": "Test Checklist"}
        checklist_response = await authenticated_client.post(
            f"/api/v1/tasks/{task_id}/checklists",
            json=checklist_data
        )
        checklist_id = checklist_response.json()["id"]
        
        item_data = {"content": "Test Item", "position": 0}
        
        # Act
        response = await authenticated_client.post(
            f"/api/v1/checklists/{checklist_id}/items",
            json=item_data
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Test Item"
        assert data["checklist_id"] == checklist_id
        assert data["is_completed"] is False
        assert data["position"] == 0
    
    @pytest.mark.asyncio
    async def test_update_checklist_item_success(
        self,
        authenticated_client: AsyncClient
    ):
        """Test successful checklist item update"""
        # Arrange - create task, checklist, and item
        task_data = {"title": "Test Task", "priority": "medium"}
        task_response = await authenticated_client.post("/api/v1/tasks/", json=task_data)
        task_id = task_response.json()["id"]
        
        checklist_data = {"title": "Test Checklist"}
        checklist_response = await authenticated_client.post(
            f"/api/v1/tasks/{task_id}/checklists",
            json=checklist_data
        )
        checklist_id = checklist_response.json()["id"]
        
        item_data = {"content": "Original Item", "position": 0}
        item_response = await authenticated_client.post(
            f"/api/v1/checklists/{checklist_id}/items",
            json=item_data
        )
        item_id = item_response.json()["id"]
        
        update_data = {"content": "Updated Item", "is_completed": True}
        
        # Act
        response = await authenticated_client.put(
            f"/api/v1/checklist-items/{item_id}",
            json=update_data
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated Item"
        assert data["is_completed"] is True
    
    @pytest.mark.asyncio
    async def test_delete_checklist_item_success(
        self,
        authenticated_client: AsyncClient
    ):
        """Test successful checklist item deletion"""
        # Arrange - create task, checklist, and item
        task_data = {"title": "Test Task", "priority": "medium"}
        task_response = await authenticated_client.post("/api/v1/tasks/", json=task_data)
        task_id = task_response.json()["id"]
        
        checklist_data = {"title": "Test Checklist"}
        checklist_response = await authenticated_client.post(
            f"/api/v1/tasks/{task_id}/checklists",
            json=checklist_data
        )
        checklist_id = checklist_response.json()["id"]
        
        item_data = {"content": "Item to Delete", "position": 0}
        item_response = await authenticated_client.post(
            f"/api/v1/checklists/{checklist_id}/items",
            json=item_data
        )
        item_id = item_response.json()["id"]
        
        # Act
        response = await authenticated_client.delete(f"/api/v1/checklist-items/{item_id}")
        
        # Assert
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_checklist_cascade_on_task_deletion(
        self,
        authenticated_client: AsyncClient
    ):
        """Test that checklists are deleted when task is deleted"""
        # Arrange - create task with checklist and items
        task_data = {"title": "Task with Checklist", "priority": "medium"}
        task_response = await authenticated_client.post("/api/v1/tasks/", json=task_data)
        task_id = task_response.json()["id"]
        
        checklist_data = {"title": "Test Checklist"}
        checklist_response = await authenticated_client.post(
            f"/api/v1/tasks/{task_id}/checklists",
            json=checklist_data
        )
        checklist_id = checklist_response.json()["id"]
        
        item_data = {"content": "Test Item", "position": 0}
        await authenticated_client.post(
            f"/api/v1/checklists/{checklist_id}/items",
            json=item_data
        )
        
        # Act - delete the task
        delete_response = await authenticated_client.delete(f"/api/v1/tasks/{task_id}")
        
        # Assert
        assert delete_response.status_code == 200
        
        # Verify checklist is also deleted (should return 404)
        checklist_get = await authenticated_client.get(f"/api/v1/checklists/{checklist_id}")
        assert checklist_get.status_code == 404

