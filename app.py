from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, selectinload
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import json

from database.database import engine, get_db
from database.models import Base, User, Payments
from database.redis_client import redis_client

app = FastAPI()

# --- JWT Settings ---
SECRET_KEY = "MY_FIRST_JWT_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- Database ---
Base.metadata.create_all(bind=engine)

# --- Schemas ---
class UserCreate(BaseModel):
    name: str
    age: int
    password: str = Field(min_length=8, max_length=72)

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    access: bool

    model_config = {"from_attributes": True}

# --- Redis ---
@app.on_event("startup")
async def startup():
    await redis_client.ping()

@app.on_event("shutdown")
async def shutdown():
    await redis_client.close()

# --- Utils ---
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def is_valid_age(age):
    return 0 <= age <= 120

def is_access(age):
    return age >= 18

# --- JWT Auth Dependency ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:

    if await redis_client.get(f"blacklist:{token}"):
        raise HTTPException(status_code=401, detail="Token revoked")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user

# --- Endpoints ---
@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if not is_valid_age(user.age):
        raise HTTPException(status_code=400, detail="Invalid age")
    
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users")
async def get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cached_users = await redis_client.get("users_all")

    if cached_users:
        return json.loads(cached_users)

    users = db.query(User).all()

    user_data = [
            {"id": u.id, "name": u.name, "age": u.age, "access": u.access}
            for u in users
        ]

    await redis_client.set(
            "users_all",
            json.dumps(user_data),
            ex=60
        )
    return users_data

@app.get("/users/{id}", response_model=UserResponse)
def get_user_by_id(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/payments")
def get_all_payments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payments = db.query(Payments).options(selectinload(Payments.user)).all()
    return payments

@app.post("/auth/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    await redis_client.set(f"blacklist:{token}", "true", ex=1800)
    return {"message": "Logged out"}
