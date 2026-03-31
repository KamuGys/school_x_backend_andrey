from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db import init_db
from app.exceptions import CommentNotFound, TaskNotFound
from app.routers import auth, files, meta, tasks
from app.services.minio_service import minio_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Lifespan START")
    try:
        await init_db()
        await minio_service.ensure_bucket()
        logger.info("DB + MinIO ready")
    except Exception as e:
        logger.error(f"Lifespan error: {e}", exc_info=True)
        raise
    yield
    logger.info("Lifespan shutdown")

app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(files.router)
app.include_router(meta.router)

@app.exception_handler(TaskNotFound)
async def task_not_found_handler(request: Request, exc: TaskNotFound):
    return JSONResponse(status_code=404, content={"detail": "Task not found"})

@app.exception_handler(CommentNotFound)
async def comment_not_found_handler(request: Request, exc: CommentNotFound):
    return JSONResponse(status_code=404, content={"detail": "Comment not found"})

@app.get("/")
async def root():
    return {"status": "ok", "message": "School X Backend running async"}