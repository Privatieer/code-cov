"""
Unit tests for ChecklistUseCase
"""
import pytest
from uuid import UUID, uuid4
from unittest.mock import AsyncMock

from backend.src.application.use_cases.checklist_use_case import ChecklistUseCase
from backend.src.application.dtos.task_dtos import ChecklistCreateDTO, ChecklistItemCreateDTO, ChecklistItemUpdateDTO
from backend.src.domain.entities.models import Checklist, ChecklistItem, Task, TaskStatus, TaskPriority
from backend.src.domain.ports.repositories.base import IChecklistRepository, ITaskRepository


@pytest.mark.unit
class TestChecklistUseCase:
    """Test cases for ChecklistUseCase"""
    
    @pytest.fixture
    def checklist_use_case(
        self,
        mock_checklist_repository: IChecklistRepository,
        mock_task_repository: ITaskRepository
    ) -> ChecklistUseCase:
        """Create a ChecklistUseCase instance with mocked dependencies"""
        return ChecklistUseCase(mock_checklist_repository, mock_task_repository)
    
    @pytest.mark.asyncio
    async def test_create_checklist_success(
        self,
        checklist_use_case: ChecklistUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_checklist_id: UUID,
        mock_task_repository: ITaskRepository,
        mock_checklist_repository: IChecklistRepository,
        sample_task: Task
    ):
        """Test successful checklist creation"""
        # Arrange
        dto = ChecklistCreateDTO(title="Test Checklist")
        
        expected_checklist = Checklist(
            id=mock_checklist_id,
            task_id=mock_task_id,
            title=dto.title
        )
        
        mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
        mock_checklist_repository.create_checklist = AsyncMock(return_value=expected_checklist)
        
        # Act
        result = await checklist_use_case.create_checklist(mock_task_id, mock_user_id, dto)
        
        # Assert
        assert result == expected_checklist
        assert result.title == "Test Checklist"
        mock_task_repository.get_by_id.assert_called_once_with(mock_task_id)
        mock_checklist_repository.create_checklist.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_checklist_task_not_found(
        self,
        checklist_use_case: ChecklistUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_task_repository: ITaskRepository
    ):
        """Test checklist creation fails when task not found"""
        # Arrange
        dto = ChecklistCreateDTO(title="Test Checklist")
        mock_task_repository.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await checklist_use_case.create_checklist(mock_task_id, mock_user_id, dto)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_checklist_wrong_user(
        self,
        checklist_use_case: ChecklistUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_task_repository: ITaskRepository
    ):
        """Test checklist creation fails for wrong user"""
        # Arrange
        other_user_id = uuid4()
        task = Task(
            id=mock_task_id,
            user_id=other_user_id,
            title="Other User's Task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM
        )
        
        dto = ChecklistCreateDTO(title="Test Checklist")
        mock_task_repository.get_by_id = AsyncMock(return_value=task)
        
        # Act
        result = await checklist_use_case.create_checklist(mock_task_id, mock_user_id, dto)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_checklist_success(
        self,
        checklist_use_case: ChecklistUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_checklist_id: UUID,
        mock_task_repository: ITaskRepository,
        mock_checklist_repository: IChecklistRepository,
        sample_task: Task,
        sample_checklist: Checklist
    ):
        """Test successful checklist deletion"""
        # Arrange
        mock_checklist_repository.get_checklist_by_id = AsyncMock(return_value=sample_checklist)
        mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
        mock_checklist_repository.delete_checklist = AsyncMock(return_value=True)
        
        # Act
        result = await checklist_use_case.delete_checklist(mock_checklist_id, mock_user_id)
        
        # Assert
        assert result is True
        mock_checklist_repository.delete_checklist.assert_called_once_with(mock_checklist_id)
    
    @pytest.mark.asyncio
    async def test_add_item_success(
        self,
        checklist_use_case: ChecklistUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_checklist_id: UUID,
        mock_task_repository: ITaskRepository,
        mock_checklist_repository: IChecklistRepository,
        sample_task: Task,
        sample_checklist: Checklist
    ):
        """Test successful item addition"""
        # Arrange
        dto = ChecklistItemCreateDTO(content="Test Item", position=0)
        
        expected_item = ChecklistItem(
            id=uuid4(),
            checklist_id=mock_checklist_id,
            content=dto.content,
            position=dto.position,
            is_completed=False
        )
        
        mock_checklist_repository.get_checklist_by_id = AsyncMock(return_value=sample_checklist)
        mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
        mock_checklist_repository.add_item = AsyncMock(return_value=expected_item)
        
        # Act
        result = await checklist_use_case.add_item(mock_checklist_id, mock_user_id, dto)
        
        # Assert
        assert result == expected_item
        assert result.content == "Test Item"
        mock_checklist_repository.add_item.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_item_success(
        self,
        checklist_use_case: ChecklistUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_checklist_id: UUID,
        mock_task_repository: ITaskRepository,
        mock_checklist_repository: IChecklistRepository,
        sample_task: Task,
        sample_checklist: Checklist
    ):
        """Test successful item update"""
        # Arrange
        item_id = uuid4()
        item = ChecklistItem(
            id=item_id,
            checklist_id=mock_checklist_id,
            content="Original Content",
            is_completed=False,
            position=0
        )
        
        dto = ChecklistItemUpdateDTO(content="Updated Content", is_completed=True)
        
        updated_item = ChecklistItem(
            id=item_id,
            checklist_id=mock_checklist_id,
            content=dto.content,
            is_completed=dto.is_completed,
            position=0
        )
        
        mock_checklist_repository.get_item_by_id = AsyncMock(return_value=item)
        mock_checklist_repository.get_checklist_by_id = AsyncMock(return_value=sample_checklist)
        mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
        mock_checklist_repository.update_item = AsyncMock(return_value=updated_item)
        
        # Act
        result = await checklist_use_case.update_item(item_id, mock_user_id, dto)
        
        # Assert
        assert result == updated_item
        assert result.content == "Updated Content"
        assert result.is_completed is True
    
    @pytest.mark.asyncio
    async def test_delete_item_success(
        self,
        checklist_use_case: ChecklistUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_checklist_id: UUID,
        mock_task_repository: ITaskRepository,
        mock_checklist_repository: IChecklistRepository,
        sample_task: Task,
        sample_checklist: Checklist
    ):
        """Test successful item deletion"""
        # Arrange
        item_id = uuid4()
        item = ChecklistItem(
            id=item_id,
            checklist_id=mock_checklist_id,
            content="Test Item",
            is_completed=False,
            position=0
        )
        
        mock_checklist_repository.get_item_by_id = AsyncMock(return_value=item)
        mock_checklist_repository.get_checklist_by_id = AsyncMock(return_value=sample_checklist)
        mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
        mock_checklist_repository.delete_item = AsyncMock(return_value=True)
        
        # Act
        result = await checklist_use_case.delete_item(item_id, mock_user_id)
        
        # Assert
        assert result is True
        mock_checklist_repository.delete_item.assert_called_once_with(item_id)

