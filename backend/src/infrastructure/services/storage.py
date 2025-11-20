import boto3
from botocore.client import Config
import asyncio
import uuid
import structlog
from backend.src.domain.ports.repositories.base import IFileStorage
from backend.src.config import settings

logger = structlog.get_logger(__name__)

class MinIOStorage(IFileStorage):
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4'),
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        # On startup, check if the bucket exists. Boto3 raises an exception if not found.
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
        except Exception as e:
            logger.error(
                "minio_storage_init_failed",
                bucket=self.bucket_name,
                error=str(e),
                endpoint=settings.S3_ENDPOINT_URL,
            )
            # In a production system you might want to handle this more gracefully
            # or ensure the bucket is created via infrastructure-as-code.
            raise

    def _upload_sync(self, file_content: bytes, key: str, content_type: str):
        """Synchronous upload logic to be run in a separate thread."""
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=file_content,
            ContentType=content_type
        )

    async def upload(self, file_content: bytes, filename: str, content_type: str) -> str:
        key = f"{uuid.uuid4()}-{filename}"
        
        try:
            await asyncio.to_thread(self._upload_sync, file_content, key, content_type)
            
            # Return the PUBLIC URL for the frontend
            url = f"{settings.S3_PUBLIC_URL}/{self.bucket_name}/{key}"
            logger.info("file_upload_success", key=key, url=url)
            return url
        except Exception as e:
            logger.error("file_upload_failed", key=key, error=str(e))
            # Propagate the error to be handled by the use case/API layer
            raise

    def _delete_sync(self, key: str):
        """Synchronous delete logic."""
        self.s3.delete_object(Bucket=self.bucket_name, Key=key)

    async def delete(self, file_url: str) -> bool:
        if not file_url:
            return False
            
        try:
            # Extract key from URL, which should be the public URL
            key = file_url.split(f"/{self.bucket_name}/")[-1]
            await asyncio.to_thread(self._delete_sync, key)
            logger.info("file_delete_success", key=key)
            return True
        except Exception as e:
            logger.error("file_delete_failed", url=file_url, error=str(e))
            return False
