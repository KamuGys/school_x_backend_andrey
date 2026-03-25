from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db, Person as PersonDB
from models import Person, PersonCreate, PersonUpdate

app = FastAPI(title="Hobby Manager API", version="1.0")

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/people/", response_model=Person, status_code=201)
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    db_person = PersonDB(
        name=person.name,
        passport=person.passport,
        hobby=person.hobby,
        level=person.level
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

@app.get("/people/", response_model=list[Person])
def read_people(db: Session = Depends(get_db)):
    return db.query(PersonDB).all()

@app.get("/people/{person_id}", response_model=Person)
def read_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(PersonDB).filter(PersonDB.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Человек не найден")
    return person

@app.put("/people/{person_id}", response_model=Person)
def update_person(person_id: int, person: PersonUpdate, db: Session = Depends(get_db)):
    db_person = db.query(PersonDB).filter(PersonDB.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Человек не найден")

    if person.name is not None:
        db_person.name = person.name
    if person.hobby is not None:
        db_person.hobby = person.hobby
    if person.level is not None:
        db_person.level = person.level

    db.commit()
    db.refresh(db_person)
    return db_person

@app.delete("/people/{person_id}", status_code=204)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(PersonDB).filter(PersonDB.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Человек не найден")
    db.delete(person)
    db.commit()
    return