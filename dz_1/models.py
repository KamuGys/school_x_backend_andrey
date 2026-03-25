from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PersonBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    passport: str = Field(..., pattern=r"^\d{10}$", description="10 цифр")
    hobby: str = Field(..., min_length=2, max_length=30)
    level: str = Field(..., pattern=r"^(новичок|средний|продвинутый)$")

    class Config:
        from_attributes = True

class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    hobby: Optional[str] = Field(None, min_length=2, max_length=30)
    level: Optional[str] = Field(None, pattern=r"^(новичок|средний|продвинутый)$")

class Person(PersonBase):
    id: int
    created_at: datetime