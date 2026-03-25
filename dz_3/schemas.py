from pydantic import BaseModel
from typing import Optional

class UserIn(BaseModel):
    email: str
    password: str

class TaskIn(BaseModel):
    title: str
    description: str
    status: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

#новый код
class CommentIn(BaseModel):
    content: str