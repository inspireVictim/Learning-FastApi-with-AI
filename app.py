from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload, selectinload

from database.database import engine, get_db
from database.models import Base, User, Payments

app = FastAPI()

#DataBase
Base.metadata.create_all(bind=engine)

#SCHEMAS
class UserCreate(BaseModel):
    name: str
    age: int
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    access: bool

    class Config:
        orm_mode = True

#UTILS
def is_valid_age(age):
    return 0 <= age <= 120

def is_access(age):
    return age >= 18

#ENDPOINTS
@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if not is_valid_age(user.age):
        raise HTTPException(status_code=400, detail="invalid age")
    
    db_user = User(
            name=user.name,
            age=user.age,
            password=user.password,
            access=is_access(user.age)
            )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
            "id": db_user.id,
            "name": db_user.name,
            "access": db_user.access
            }

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.get("/users/{id}", response_model=UserResponse)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.get("/payments")
def get_all_payments(db: Session = Depends(get_db)):
    payments = db.query(Payments).options(selectinload(Payments.user)).all()
    return payments
