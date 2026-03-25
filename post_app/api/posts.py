from typing import List, Annotated

from fastapi import APIRouter, Depends, UploadFile, File, Form
from starlette.responses import JSONResponse

from services import PostService
from schemas import PostCreateSchema, PostInfoSchema
from dependency import CurrentUserDep

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/")
def create_post(
    current_user: CurrentUserDep,
    post_text: Annotated[str, Form(min_length=1, max_length=10000)],
    image: Annotated[UploadFile | None, File()] = None,
    service: PostService = Depends(PostService),
) -> PostInfoSchema:
    return service.create_post(post_text, current_user.id, image)


@router.get("/")
def get_posts(
    service: PostService = Depends(PostService),
) -> List[PostInfoSchema]:
    return service.get_all_posts()

@router.get("/{id}")
def get_post(
    id: int,
    service: PostService = Depends(PostService),
) -> PostInfoSchema:
    return service.get_post(id)


@router.delete("/{id}")
def delete_post(
    post_id: int,
    current_user: CurrentUserDep,
    service: PostService = Depends(PostService)
) -> JSONResponse:
    service.delete_post(post_id, current_user.id)
    return JSONResponse(status_code=200, content={"message": "Пост удален"})