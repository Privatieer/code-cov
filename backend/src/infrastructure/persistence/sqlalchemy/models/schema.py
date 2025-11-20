from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, Boolean, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID, ARRAY as PG_ARRAY
from sqlalchemy.orm import relationship
import uuid
import json
from datetime import datetime, timezone
from sqlalchemy.sql import func
from backend.src.infrastructure.persistence.sqlalchemy.database import Base

def utc_now():
    return datetime.now(timezone.utc)


class StringArray(TypeDecorator):
    """
    A database-agnostic type for storing arrays of strings.
    Uses PostgreSQL ARRAY for PostgreSQL and JSON for SQLite.
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_ARRAY(String))
        elif dialect.name == 'sqlite':
            return dialect.type_descriptor(Text)
        else:
            return dialect.type_descriptor(Text)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        elif dialect.name == 'sqlite':
            return json.dumps(value) if isinstance(value, list) else value
        else:
            return json.dumps(value) if isinstance(value, list) else value

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        if dialect.name == 'postgresql':
            return value if value else []
        elif dialect.name == 'sqlite':
            if isinstance(value, str):
                try:
                    return json.loads(value) if value else []
                except (json.JSONDecodeError, TypeError):
                    return []
            return value if value else []
        else:
            if isinstance(value, str):
                try:
                    return json.loads(value) if value else []
                except (json.JSONDecodeError, TypeError):
                    return []
            return value if value else []

class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=utc_now)

    tasks = relationship("TaskModel", back_populates="user", cascade="all, delete-orphan")
    task_lists = relationship("TaskListModel", back_populates="user", cascade="all, delete-orphan")

class TaskListModel(Base):
    __tablename__ = "task_lists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=utc_now)

    user = relationship("UserModel", back_populates="task_lists")
    tasks = relationship("TaskModel", back_populates="task_list", cascade="all, delete-orphan")

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    task_list_id = Column(UUID(as_uuid=True), ForeignKey("task_lists.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="todo", index=True)
    priority = Column(String, default="medium")
    due_date = Column(DateTime, nullable=True)
    tags = Column(StringArray, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=utc_now)

    user = relationship("UserModel", back_populates="tasks")
    task_list = relationship("TaskListModel", back_populates="tasks")
    attachments = relationship("AttachmentModel", back_populates="task", cascade="all, delete-orphan")
    checklists = relationship("ChecklistModel", back_populates="task", cascade="all, delete-orphan")

class ChecklistModel(Base):
    __tablename__ = "checklists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=utc_now)

    task = relationship("TaskModel", back_populates="checklists")
    items = relationship("ChecklistItemModel", back_populates="checklist", cascade="all, delete-orphan")

class ChecklistItemModel(Base):
    __tablename__ = "checklist_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    checklist_id = Column(UUID(as_uuid=True), ForeignKey("checklists.id"), nullable=False)
    content = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    position = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    checklist = relationship("ChecklistModel", back_populates="items")

class AttachmentModel(Base):
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("TaskModel", back_populates="attachments")

