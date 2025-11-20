from celery import Celery
from backend.src.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# In a real app, we'd auto-discover tasks
celery_app.autodiscover_tasks(["backend.src.infrastructure.services.worker"])
