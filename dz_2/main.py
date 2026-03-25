#app
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from typing import Optional

#app DB
engine = create_engine("sqlite:///./db.sqlite", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
def get_db(): db=SessionLocal(); yield db; db.close()

#app MODELS
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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)

#app SCHEMAS
class UserIn(BaseModel): email:str; password:str
class TaskIn(BaseModel): title:str; description:str; status:Optional[str]=None
class TaskUpdate(BaseModel): title:Optional[str]=None; description:Optional[str]=None; status:Optional[str]=None

#app SECURITY
pwd = CryptContext(schemes=["bcrypt"])
SECRET, ALG = "SECRET", "HS256"
def hash_password(p): return pwd.hash(p)
def verify_password(p,h): return pwd.verify(p,h)
def create_token(uid:int): return jwt.encode({"id":uid,"exp":datetime.now(timezone.utc)+timedelta(hours=2)}, SECRET, ALG)

def current_user(authorization:str=Header(...), db:Session=Depends(get_db)):
    try:
        token = authorization.split()[1]
        data = jwt.decode(token, SECRET, algorithms=[ALG])
        user = db.query(User).filter(User.id==data["id"]).first()
        if not user: raise
        return user
    except: raise HTTPException(401,"Unauthorized")

#app REPOS
class UserRepo:
    def __init__(self, db): self.db=db
    def get(self,email): return self.db.query(User).filter(User.email==email).first()
    def create(self,email,password): u=User(email=email,password=password); self.db.add(u); self.db.commit(); self.db.refresh(u); return u

class TaskRepo:
    def __init__(self,db): self.db=db
    def create(self,d): t=Task(**d.model_dump()); self.db.add(t); self.db.commit(); self.db.refresh(t); return t
    def all(self): return self.db.query(Task).all()
    def get(self,id): return self.db.query(Task).filter(Task.id==id).first()
    def update(self,t,d): 
        for k,v in d.model_dump(exclude_unset=True).items(): setattr(t,k,v)
        self.db.commit(); self.db.refresh(t); return t
    def delete(self,t): self.db.delete(t); self.db.commit()

#app APP
app = FastAPI()

#app AUTH
@app.post("/auth/register")
def register(d:UserIn, db:Session=Depends(get_db)):
    r = UserRepo(db)
    if r.get(d.email): raise HTTPException(400,"exists")
    return {"id": r.create(d.email, hash_password(d.password)).id}

@app.post("/auth/login")
def login(d:UserIn, db:Session=Depends(get_db)):
    r = UserRepo(db)
    u = r.get(d.email)
    if not u or not verify_password(d.password,u.password): raise HTTPException(400,"wrong")
    return {"access_token": create_token(u.id)}

#app TASKS (protected)
@app.post("/tasks/")
def create_task(d:TaskIn, db:Session=Depends(get_db), u=Depends(current_user)): return TaskRepo(db).create(d)

@app.get("/tasks/")
def list_tasks(db:Session=Depends(get_db), u=Depends(current_user)): return TaskRepo(db).all()

@app.get("/tasks/{id}")
def get_task(id:int, db:Session=Depends(get_db), u=Depends(current_user)):
    t = TaskRepo(db).get(id)
    if not t: raise HTTPException(404)
    return t

@app.put("/tasks/{id}")
def update_task(id:int, d:TaskUpdate, db:Session=Depends(get_db), u=Depends(current_user)):
    r = TaskRepo(db); t = r.get(id)
    if not t: raise HTTPException(404)
    return r.update(t,d)

@app.delete("/tasks/{id}")
def delete_task(id:int, db:Session=Depends(get_db), u=Depends(current_user)):
    r = TaskRepo(db); t = r.get(id)
    if not t: raise HTTPException(404)
    r.delete(t)
    return {"ok":True}