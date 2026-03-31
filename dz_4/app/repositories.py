from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import CommentNotFound, TaskNotFound
from .models import Comment, Task, User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str):
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, email: str, password: str) -> User:
        user = User(email=email, password=password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data) -> Task:
        task = Task(**data.model_dump())
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def all(self):
        result = await self.session.execute(select(Task).order_by(Task.id.desc()))
        return result.scalars().all()

    async def get(self, task_id: int) -> Task:
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise TaskNotFound()
        return task

    async def update(self, task: Task, data) -> Task:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)
        await self.session.commit()


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task_id: int, content: str) -> Comment:
        comment = Comment(task_id=task_id, content=content)
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def by_task(self, task_id: int):
        result = await self.session.execute(select(Comment).where(Comment.task_id == task_id).order_by(Comment.id.asc()))
        return result.scalars().all()

    async def get(self, comment_id: int) -> Comment:
        result = await self.session.execute(select(Comment).where(Comment.id == comment_id))
        comment = result.scalar_one_or_none()
        if not comment:
            raise CommentNotFound()
        return comment