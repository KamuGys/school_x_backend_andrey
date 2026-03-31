from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..db import get_session
from ..services.minio_service import minio_service

router = APIRouter(tags=["meta"])


@router.get("/health")
async def health(session: AsyncSession = Depends(get_session)):
    db_ok = True
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    minio_ok = await minio_service.healthcheck()
    status_code = 200 if db_ok and minio_ok else 503

    return JSONResponse(
        status_code=status_code,
        content={"db": db_ok, "minio": minio_ok},
    )


@router.get("/info")
async def info():
    return {"version": settings.app_version, "environment": settings.environment}