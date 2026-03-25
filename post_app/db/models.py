from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String

from post_app.core.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))