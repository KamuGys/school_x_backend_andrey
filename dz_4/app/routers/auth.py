from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..schemas import TokenOut, UserCreate
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(data: UserCreate, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    try:
        user = await service.register(data.email, data.password)
        return {"id": user.id, "email": user.email}
    except ValueError as e:
        if str(e) == "User exists":
            raise HTTPException(status_code=400, detail="User exists")
        raise


@router.post("/login", response_model=TokenOut)
async def login(data: UserCreate, session: AsyncSession = Depends(get_session)):
    service = AuthService(session)
    try:
        return await service.login(data.email, data.password)
    except ValueError:
        raise HTTPException(status_code=400, detail="Wrong credentials")