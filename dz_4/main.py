from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .app.core.config import settings
from .app.db import init_db
from .app.exceptions import CommentNotFound, TaskNotFound
from .routers import auth, files, meta, tasks
from .app.services.minio_service import minio_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await minio_service.ensure_bucket()
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(files.router)
app.include_router(meta.router)


@app.exception_handler(TaskNotFound)
async def task_not_found_handler(_: Request, __: TaskNotFound):
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "TaskNotFound", "message": "Task not found"}},
    )


@app.exception_handler(CommentNotFound)
async def comment_not_found_handler(_: Request, __: CommentNotFound):
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "CommentNotFound", "message": "Comment not found"}},
    )