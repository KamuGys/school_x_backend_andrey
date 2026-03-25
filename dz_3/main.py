from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from unittest.mock import Mock

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    content = Column(String)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

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

class CommentIn(BaseModel):
    content: str

class TaskNotFound(Exception):
    pass

engine = create_engine("sqlite:///./db.sqlite", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

pwd = CryptContext(schemes=["bcrypt"])
SECRET = "SECRET"

def get_db():
    db = SessionLocal()
    yield db
    db.close()

def hash_password(p): return pwd.hash(p)
def create_token(uid): return jwt.encode({"id": uid}, SECRET, algorithm="HS256")

def current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    try:
        token = authorization.split()[1]
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        user = db.query(User).filter(User.id == data["id"]).first()
        if not user: raise Exception()
        return user
    except: raise HTTPException(401, "Unauthorized")

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

class CommentRepo:
    def __init__(self, db): self.db = db
    def create(self, task_id, content):
        c = Comment(task_id=task_id, content=content)
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)
        return c
    def by_task(self, task_id):
        return self.db.query(Comment).filter(Comment.task_id == task_id).all()

class TaskService:
    def __init__(self, repo): self.repo = repo
    def create_task(self, data): return self.repo.create(data)

app = FastAPI()

@app.post("/auth/register")
def register(data: UserIn, db: Session = Depends(get_db)):
    repo = UserRepo(db)
    if repo.get(data.email): raise HTTPException(400, "User exists")
    user = repo.create(data.email, hash_password(data.password))
    return {"id": user.id}

@app.post("/auth/login")
def login(data: UserIn, db: Session = Depends(get_db)):
    repo = UserRepo(db)
    user = repo.get(data.email)
    if not user or not pwd.verify(data.password, user.password): raise HTTPException(400, "Wrong credentials")
    return {"access_token": create_token(user.id)}

@app.post("/tasks/")
def create_task(data: TaskIn, db: Session = Depends(get_db), user=Depends(current_user)):
    repo = TaskRepo(db)
    return repo.create(data)

@app.get("/tasks/")
def get_tasks(db: Session = Depends(get_db), user=Depends(current_user)):
    repo = TaskRepo(db)
    return repo.all()

@app.get("/tasks/{id}")
def get_task(id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    repo = TaskRepo(db)
    try: return repo.get(id)
    except TaskNotFound: raise HTTPException(404, {"error": {"code": "TaskNotFound", "message": "Task not found"}})

@app.put("/tasks/{id}")
def update_task(id: int, data: TaskUpdate, db: Session = Depends(get_db), user=Depends(current_user)):
    repo = TaskRepo(db)
    try:
        task = repo.get(id)
        return repo.update(task, data)
    except TaskNotFound: raise HTTPException(404, {"error": {"code": "TaskNotFound", "message": "Task not found"}})

@app.delete("/tasks/{id}")
def delete_task(id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    repo = TaskRepo(db)
    try:
        task = repo.get(id)
        repo.delete(task)
        return {"ok": True}
    except TaskNotFound: raise HTTPException(404, {"error": {"code": "TaskNotFound", "message": "Task not found"}})

@app.post("/v1/tasks/{task_id}/comments")
def create_comment(task_id: int, data: CommentIn, db: Session = Depends(get_db), user=Depends(current_user)):
    task_repo = TaskRepo(db)
    try: task_repo.get(task_id)
    except TaskNotFound: raise HTTPException(404, {"error": {"code": "TaskNotFound", "message": "Task not found"}})
    comment_repo = CommentRepo(db)
    return comment_repo.create(task_id, data.content)

@app.get("/v1/tasks/{task_id}/comments")
def get_comments(task_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    task_repo = TaskRepo(db)
    try: task_repo.get(task_id)
    except TaskNotFound: raise HTTPException(404, {"error": {"code": "TaskNotFound", "message": "Task not found"}})
    comment_repo = CommentRepo(db)
    return comment_repo.by_task(task_id)

def test_task_service_create_task():
    mock_repo = Mock()
    service = TaskService(mock_repo)
    task_data = TaskIn(title="Unit", description="Test")
    mock_repo.create.return_value = type('Task', (), {"id": 1, "title": "Unit"})()
    result = service.create_task(task_data)
    mock_repo.create.assert_called_once_with(task_data)
    return result.title == "Unit"

def test_integration_create_task(client, headers):
    r = client.post("/tasks/", headers=headers, json={"title": "Integration", "description": "Test"})
    return r.status_code == 200

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)