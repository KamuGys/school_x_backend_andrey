from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.post_service import PostService
from app.services.s3_service import S3Service

router = APIRouter()


@router.post("/posts")
async def create_post(
    title: str,
    content: str,
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):

    service = PostService(db)
    s3 = S3Service()

    image_url = None

    if file:
        try:
            file_content = await file.read()
            image_url = await s3.upload_file(file_content, file.filename)
        except Exception as e:
            print("file error", e)

    post = await service.create_post(title, content, image_url)

    if not post:
        return {"error": "something went wrong"}

    return post


@router.get("/posts")
async def get_posts(db: AsyncSession = Depends(get_db)):

    service = PostService(db)

    posts = await service.get_posts()

    return posts