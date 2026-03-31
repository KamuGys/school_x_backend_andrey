from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..security import get_current_user
from ..services.minio_service import minio_service
from ..services.task_service import TaskService

router = APIRouter(tags=["files"])


@router.post("/v1/tasks/{task_id}/upload-avatar")
async def upload_avatar(
    task_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    _user=Depends(get_current_user),
):
    task_service = TaskService(session)
    try:
        await task_service.get_task(task_id)
    except Exception:
        raise HTTPException(status_code=404, detail={"error": {"code": "TaskNotFound", "message": "Task not found"}})

    url = await minio_service.upload_avatar(task_id, file)
    return {"task_id": task_id, "url": url}