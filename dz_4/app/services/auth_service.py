from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories import UserRepository
from ..security import create_token, hash_password, verify_password


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def register(self, email: str, password: str):
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ValueError("User exists")
        user = await self.repo.create(email=email, password=hash_password(password))
        return user

    async def login(self, email: str, password: str):
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password):
            raise ValueError("Wrong credentials")
        return {"access_token": create_token(user.id), "token_type": "bearer"}