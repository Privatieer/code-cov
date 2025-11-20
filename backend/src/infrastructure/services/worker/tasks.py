from backend.src.infrastructure.services.worker.celery_app import celery_app
from backend.src.infrastructure.persistence.sqlalchemy.database import AsyncSessionLocal
from backend.src.infrastructure.persistence.sqlalchemy.repositories.task_repository import SQLAlchemyTaskRepository
import asyncio
import structlog

logger = structlog.get_logger()

@celery_app.task
def check_due_tasks():
    """
    Periodic task to check for tasks due in the next 24 hours.
    Since Celery is sync by default, we bridge to async.
    """
    asyncio.run(_check_due_tasks_async())

async def _check_due_tasks_async():
    logger.info("Starting check_due_tasks job")
    async with AsyncSessionLocal() as session:
        repo = SQLAlchemyTaskRepository(session)
        due_tasks = await repo.get_due_soon(hours=24)
        
        for task in due_tasks:
            # Idempotency check would go here (e.g. check if notification already sent in Redis)
            # For now we just log
            logger.info(
                "Reminder Sent", 
                task_id=str(task.id), 
                user_id=str(task.user_id), 
                title=task.title, 
                event="reminder_sent"
            )

