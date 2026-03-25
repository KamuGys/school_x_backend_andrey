from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import engine
from post_app.db.models import Post
from sqlalchemy import select

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/posts")
async def create_post(title: str, db: AsyncSession = Depends(get_db)):
    post = Post(title=title)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@app.get("/posts")
async def get_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post))
    return result.scalars().all()