from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from post_app.db.models import Post


class PostService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_post(self, title, content, image_url=None):

        post = Post(
            title=title,
            content=content,
            image_url=image_url
        )

        self.db.add(post)

        try:
            await self.db.commit()
            await self.db.refresh(post)
            return post
        except Exception as e:
            await self.db.rollback()
            print("db error:", e)
            return None

    async def get_posts(self):
        result = await self.db.execute(select(Post))
        return result.scalars().all()