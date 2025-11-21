import asyncio
import structlog
from backend.src.infrastructure.persistence.sqlalchemy.database import AsyncSessionLocal, engine, Base
from backend.src.infrastructure.persistence.sqlalchemy.repositories.user_repository import SQLAlchemyUserRepository
from backend.src.infrastructure.security.hashing import get_password_hash
from backend.src.domain.entities.models import User, UserRole
# Import models to register them with Base
from backend.src.infrastructure.persistence.sqlalchemy.models.schema import (
    UserModel, TaskModel, AttachmentModel, TaskListModel, ChecklistModel, ChecklistItemModel
)

log = structlog.get_logger()

async def init_db_data():
    # Create tables
    log.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Database tables created.")

    async with AsyncSessionLocal() as session:
        repo = SQLAlchemyUserRepository(session)
        
        # Check if admin exists
        admin_email = "admin@example.com"
        admin_password = "admin123"
        existing_admin = await repo.get_by_email(admin_email)
        
        if not existing_admin:
            log.info(f"Creating default admin user: {admin_email}")
            admin_user = User(
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                role=UserRole.ADMIN,
                is_verified=True
            )
            created_user = await repo.create(admin_user)
            log.info(f"Admin user created successfully. ID: {created_user.id}")
        else:
            # Update password hash in case it changed or database was reset
            log.info("Default admin user already exists. Updating password hash...")
            existing_admin.password_hash = get_password_hash(admin_password)
            existing_admin.is_verified = True
            await repo.update(existing_admin)
            log.info("Admin password updated successfully.")
            

        # Check if admin exists
        user_email = "user@example.com"
        user_password = "user123"
        existing_user = await repo.get_by_email(user_email)
        
        if not existing_user:
            log.info(f"Creating default user: {user_email}")
            user_user = User(
                email=user_email,
                password_hash=get_password_hash(user_password),
                role=UserRole.USER,
                is_verified=True
            )
            created_user = await repo.create(user_user)
            log.info(f"User created successfully. ID: {created_user.id}")
        else:
            # Update password hash in case it changed or database was reset
            log.info("Default user already exists. Updating password hash...")
            existing_user.password_hash = get_password_hash(user_password)
            existing_user.is_verified = True
            await repo.update(existing_user)
            log.info("User password updated successfully.")

if __name__ == "__main__":
    asyncio.run(init_db_data())

