from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TaskCreate(BaseModel):
    title: str
    description: str
    status: Optional[str] = "pending"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: str
    created_at: str


class CommentCreate(BaseModel):
    content: str


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    task_id: int
    created_at: str


class UploadAvatarResponse(BaseModel):
    task_id: int
    url: str


class HealthResponse(BaseModel):
    db: bool
    minio: bool


class InfoResponse(BaseModel):
    version: str
    environment: str