from sqlalchemy.orm import Session
from models import User, Task, Comment
from schemas import TaskIn, CommentIn
from exceptions import TaskNotFound

class UserRepo:
    def __init__(self, db): self.db = db
    def get(self, email): return self.db.query(User).filter(User.email == email).first()
    def create(self, email, password): 
        u = User(email=email, password=password)
        self.db.add(u)
        self.db.commit()
        self.db.refresh(u)
        return u

class TaskRepo:
    def __init__(self, db): self.db = db
    def create(self, data): 
        t = Task(**data.dict())
        self.db.add(t)
        self.db.commit()
        self.db.refresh(t)
        return t
    def all(self): return self.db.query(Task).all()
    def get(self, id): 
        task = self.db.query(Task).filter(Task.id == id).first()
        if not task: raise TaskNotFound()
        return task
    def update(self, task, data): 
        for k, v in data.dict(exclude_unset=True).items(): setattr(task, k, v)
        self.db.commit()
        self.db.refresh(task)
        return task
    def delete(self, task): 
        self.db.delete(task)
        self.db.commit()

#новый код
class CommentRepo:
    def __init__(self, db): self.db = db
    def create(self, task_id, content): 
        c = Comment(task_id=task_id, content=content)
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)
        return c
    def by_task(self, task_id): 
        comments = self.db.query(Comment).filter(Comment.task_id == task_id).all()
        return comments

#новый код
class TaskService:
    def __init__(self, repo): self.repo = repo
    def create_task(self, data): return self.repo.create(data)