"""
Unit tests for TaskUseCase
"""
import pytest
from uuid import UUID, uuid4
from unittest.mock import AsyncMock

from backend.src.application.use_cases.task_use_case import TaskUseCase
from backend.src.application.dtos.task_dtos import TaskCreateDTO, TaskUpdateDTO
from backend.src.domain.entities.models import Task, TaskStatus, TaskPriority, Attachment
from backend.src.domain.ports.repositories.base import ITaskRepository, IFileStorage, ITaskListRepository


@pytest.mark.unit
class TestTaskUseCase:
    """Test cases for TaskUseCase"""
    
    @pytest.fixture
    def task_use_case(
        self,
        mock_task_repository: ITaskRepository,
        mock_file_storage: IFileStorage
    ) -> TaskUseCase:
        """Create a TaskUseCase instance with mocked dependencies"""
        return TaskUseCase(mock_task_repository, mock_file_storage)
    
    @pytest.mark.asyncio
    async def test_create_task_success(
        self,
        task_use_case: TaskUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_task_repository: ITaskRepository
    ):
        """Test successful task creation"""
        # Arrange
        dto = TaskCreateDTO(
            title="Test Task",
            description="Test Description",
            priority=TaskPriority.MEDIUM
        )
        
        expected_task = Task(
            id=mock_task_id,
            user_id=mock_user_id,
            title=dto.title,
            description=dto.description,
            priority=dto.priority,
            status=TaskStatus.TODO
        )
        
        mock_task_repository.create = AsyncMock(return_value=expected_task)
        
        # Act
        result = await task_use_case.create_task(mock_user_id, dto)
        
        # Assert
        assert result == expected_task
        assert result.title == "Test Task"
        assert result.user_id == mock_user_id
        mock_task_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_task_with_invalid_task_list(
        self,
        task_use_case: TaskUseCase,
        mock_user_id: UUID,
        mock_task_repository: ITaskRepository
    ):
        """Test task creation fails with invalid task list"""
        # Arrange
        invalid_task_list_id = uuid4()
        dto = TaskCreateDTO(
            title="Test Task",
            task_list_id=invalid_task_list_id
        )
        
        mock_task_list_repo = AsyncMock(spec=ITaskListRepository)
        mock_task_list_repo.get_by_id = AsyncMock(return_value=None)
        
        task_use_case.task_list_repo = mock_task_list_repo
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid task list ID"):
            await task_use_case.create_task(mock_user_id, dto)
    
    @pytest.mark.asyncio
    async def test_get_user_tasks(
        self,
        task_use_case: TaskUseCase,
        mock_user_id: UUID,
        mock_task_repository: ITaskRepository,
        sample_task: Task
    ):
        """Test retrieving user tasks"""
        # Arrange
        expected_tasks = [sample_task]
        mock_task_repository.list_by_user = AsyncMock(return_value=expected_tasks)
        
        # Act
        result = await task_use_case.get_user_tasks(mock_user_id, {}, 20, 0)
        
        # Assert
        assert result == expected_tasks
        assert len(result) == 1
        mock_task_repository.list_by_user.assert_called_once_with(
            mock_user_id, {}, 20, 0
        )
    
    @pytest.mark.asyncio
    async def test_get_task_success(
        self,
        task_use_case: TaskUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_task_repository: ITaskRepository,
        sample_task: Task
    ):
        """Test successful task retrieval"""
        # Arrange
        mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
        
        # Act
        result = await task_use_case.get_task(mock_task_id, mock_user_id)
        
        # Assert
        assert result == sample_task
        mock_task_repository.get_by_id.assert_called_once_with(mock_task_id)
    
    @pytest.mark.asyncio
    async def test_get_task_wrong_user(
        self,
        task_use_case: TaskUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_task_repository: ITaskRepository
    ):
        """Test task retrieval fails for wrong user"""
        # Arrange
        other_user_id = uuid4()
        task = Task(
            id=mock_task_id,
            user_id=other_user_id,
            title="Other User's Task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM
        )
        mock_task_repository.get_by_id = AsyncMock(return_value=task)
        
        # Act
        result = await task_use_case.get_task(mock_task_id, mock_user_id)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_task_success(
        self,
        task_use_case: TaskUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_task_repository: ITaskRepository,
        sample_task: Task
    ):
        """Test successful task update"""
        # Arrange
        dto = TaskUpdateDTO(
            title="Updated Title",
            status=TaskStatus.IN_PROGRESS
        )
        
        updated_task = Task(
            id=mock_task_id,
            user_id=mock_user_id,
            title=dto.title,
            status=dto.status,
            priority=TaskPriority.MEDIUM
        )
        
        mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
        mock_task_repository.update = AsyncMock(return_value=updated_task)
        
        # Act
        result = await task_use_case.update_task(mock_task_id, mock_user_id, dto)
        
        # Assert
        assert result == updated_task
        assert result.title == "Updated Title"
        assert result.status == TaskStatus.IN_PROGRESS
    
    @pytest.mark.asyncio
    async def test_delete_task_success(
        self,
        task_use_case: TaskUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_task_repository: ITaskRepository,
        sample_task: Task,
        mock_file_storage: IFileStorage
    ):
        """Test successful task deletion"""
        # Arrange
        attachment = Attachment(
            id=uuid4(),
            task_id=mock_task_id,
            filename="test.pdf",
            file_url="https://example.com/test.pdf",
            file_size_bytes=1000,
            content_type="application/pdf"
        )
        sample_task.attachments = [attachment]
        
        mock_task_repository.get_by_id = AsyncMock(return_value=sample_task)
        mock_task_repository.delete = AsyncMock(return_value=True)
        
        # Act
        result = await task_use_case.delete_task(mock_task_id, mock_user_id)
        
        # Assert
        assert result is True
        mock_file_storage.delete.assert_called_once_with(attachment.file_url)
        mock_task_repository.delete.assert_called_once_with(mock_task_id)
    
    @pytest.mark.asyncio
    async def test_delete_task_not_found(
        self,
        task_use_case: TaskUseCase,
        mock_user_id: UUID,
        mock_task_id: UUID,
        mock_task_repository: ITaskRepository
    ):
        """Test task deletion fails when task not found"""
        # Arrange
        mock_task_repository.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await task_use_case.delete_task(mock_task_id, mock_user_id)
        
        # Assert
        assert result is False
        mock_task_repository.delete.assert_not_called()

