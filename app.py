from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload, selectinload
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from database.database import engine, get_db
from database.models import Base, User, Payments

app = FastAPI()


#JWT
SECRET_KEY = "MY_FIRST_JWT_SECRET_KEY"
ALGOTITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

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

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#ENDPOINTS
@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if not is_valid_age(user.age):
        raise HTTPException(status_code=400, detail="invalid age")
    
    db_user = User(
            name=user.name,
            age=user.age,
            password=hash_password(user.password),
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

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code = 401, detail = "Unauthorized")
                    
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type":"bearer"}


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
