from fastapi import Header, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from models import User
from repositories import UserRepo

pwd = CryptContext(schemes=["bcrypt"])
SECRET = "SECRET"

def hash_password(p): return pwd.hash(p)
def create_token(uid): return jwt.encode({"id":uid}, SECRET, algorithm="HS256")

def current_user(auth: str = Header(...), db: Session = Depends(lambda: None)):
    try:
        token = auth.split()[1]
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        user = db.query(User).filter(User.id == data["id"]).first()
        if not user: raise Exception("Unauthorized")
        return user
    except: raise Exception("Unauthorized")