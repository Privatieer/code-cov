from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.infrastructure.persistence.sqlalchemy.database import get_db as get_db_session
from backend.src.infrastructure.persistence.sqlalchemy.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from backend.src.infrastructure.persistence.sqlalchemy.repositories.task_repository import (
    SQLAlchemyTaskRepository,
)
from backend.src.infrastructure.persistence.sqlalchemy.repositories.task_list_repository import (
    SQLAlchemyTaskListRepository
)
from backend.src.infrastructure.persistence.sqlalchemy.repositories.checklist_repository import (
    SQLAlchemyChecklistRepository
)
from backend.src.domain.ports.repositories.base import (
    IUserRepository,
    ITaskRepository,
    IFileStorage,
    ITaskListRepository,
    IChecklistRepository
)
from backend.src.application.use_cases.auth_use_case import AuthUseCase
from backend.src.application.use_cases.task_use_case import TaskUseCase
from backend.src.application.use_cases.task_list_use_case import TaskListUseCase
from backend.src.application.use_cases.checklist_use_case import ChecklistUseCase
from backend.src.infrastructure.security.jwt_token import decode_access_token
from backend.src.infrastructure.services.storage import MinIOStorage

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_user_repo(
    session: AsyncSession = Depends(get_db_session),
) -> IUserRepository:
    return SQLAlchemyUserRepository(session)

async def get_task_repo(
    session: AsyncSession = Depends(get_db_session),
) -> ITaskRepository:
    return SQLAlchemyTaskRepository(session)

async def get_task_list_repo(
    session: AsyncSession = Depends(get_db_session),
) -> ITaskListRepository:
    return SQLAlchemyTaskListRepository(session)

async def get_checklist_repo(
    session: AsyncSession = Depends(get_db_session),
) -> IChecklistRepository:
    return SQLAlchemyChecklistRepository(session)

def get_file_storage() -> IFileStorage:
    return MinIOStorage()

async def get_auth_use_case(
    user_repo: IUserRepository = Depends(get_user_repo),
) -> AuthUseCase:
    return AuthUseCase(user_repo)

async def get_task_use_case(
    task_repo: ITaskRepository = Depends(get_task_repo),
    file_storage: IFileStorage = Depends(get_file_storage),
    task_list_repo: ITaskListRepository = Depends(get_task_list_repo)
) -> TaskUseCase:
    return TaskUseCase(task_repo, file_storage, task_list_repo)

async def get_task_list_use_case(
    task_list_repo: ITaskListRepository = Depends(get_task_list_repo)
) -> TaskListUseCase:
    return TaskListUseCase(task_list_repo)

async def get_checklist_use_case(
    checklist_repo: IChecklistRepository = Depends(get_checklist_repo),
    task_repo: ITaskRepository = Depends(get_task_repo)
) -> ChecklistUseCase:
    return ChecklistUseCase(checklist_repo, task_repo)


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    return user_id

