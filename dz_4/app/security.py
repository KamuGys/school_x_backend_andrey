from fastapi import Depends, Header, HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .core.config import settings
from .db import get_session
from .models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_token(user_id: int) -> str:
    return jwt.encode({"id": user_id}, settings.secret_key, algorithm=settings.algorithm)


async def get_current_user(
    authorization: str = Header(...),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        token = authorization.split()[1]
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("id")
        if not user_id:
            raise ValueError("Missing user id")
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        return user
    except (IndexError, JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Unauthorized")