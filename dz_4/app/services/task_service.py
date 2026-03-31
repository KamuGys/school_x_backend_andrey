from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories import CommentRepository, TaskRepository


class TaskService:
    def __init__(self, session: AsyncSession):
        self.tasks = TaskRepository(session)
        self.comments = CommentRepository(session)

    async def create_task(self, data):
        return await self.tasks.create(data)

    async def list_tasks(self):
        return await self.tasks.all()

    async def get_task(self, task_id: int):
        return await self.tasks.get(task_id)

    async def update_task(self, task_id: int, data):
        task = await self.tasks.get(task_id)
        return await self.tasks.update(task, data)

    async def delete_task(self, task_id: int):
        task = await self.tasks.get(task_id)
        await self.tasks.delete(task)

    async def create_comment(self, task_id: int, content: str):
        await self.tasks.get(task_id)
        return await self.comments.create(task_id, content)

    async def list_comments(self, task_id: int):
        await self.tasks.get(task_id)
        return await self.comments.by_task(task_id)