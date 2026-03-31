import asyncio
import io
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from minio import Minio

from ..core.config import settings


class MinioService:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket = settings.minio_bucket

    async def ensure_bucket(self) -> None:
        def _ensure():
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)

        await asyncio.to_thread(_ensure)

    async def upload_avatar(self, task_id: int, file: UploadFile) -> str:
        content = await file.read()
        suffix = Path(file.filename or "").suffix or ".bin"
        object_name = f"tasks/{task_id}/avatar-{uuid4().hex}{suffix}"

        def _upload():
            self.client.put_object(
                self.bucket,
                object_name,
                io.BytesIO(content),
                length=len(content),
                content_type=file.content_type or "application/octet-stream",
            )
            return self.client.presigned_get_object(self.bucket, object_name)

        return await asyncio.to_thread(_upload)

    async def healthcheck(self) -> bool:
        try:
            return await asyncio.to_thread(self.client.bucket_exists, self.bucket)
        except Exception:
            return False


minio_service = MinioService()