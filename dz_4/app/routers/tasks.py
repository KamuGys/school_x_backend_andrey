from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..schemas import CommentCreate, TaskCreate, TaskUpdate
from ..security import get_current_user
from ..services.task_service import TaskService

router = APIRouter(tags=["tasks"])


@router.post("/tasks/")
async def create_task(
    data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    _user=Depends(get_current_user),
):
    service = TaskService(session)
    return await service.create_task(data)


@router.get("/tasks/")
async def get_tasks(
    session: AsyncSession = Depends(get_session),
    _user=Depends(get_current_user),
):
    service = TaskService(session)
    return await service.list_tasks()


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    _user=Depends(get_current_user),
):
    service = TaskService(session)
    return await service.get_task(task_id)


@router.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    _user=Depends(get_current_user),
):
    service = TaskService(session)
    return await service.update_task(task_id, data)


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    _user=Depends(get_current_user),
):
    service = TaskService(session)
    await service.delete_task(task_id)
    return {"ok": True}


@router.post("/v1/tasks/{task_id}/comments")
async def create_comment(
    task_id: int,
    data: CommentCreate,
    session: AsyncSession = Depends(get_session),
    _user=Depends(get_current_user),
):
    service = TaskService(session)
    return await service.create_comment(task_id, data.content)


@router.get("/v1/tasks/{task_id}/comments")
async def get_comments(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    _user=Depends(get_current_user),
):
    service = TaskService(session)
    return await service.list_comments(task_id)