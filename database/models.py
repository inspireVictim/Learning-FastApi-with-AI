from sqlalchemy import Column, Integer, String, Boolean
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index = True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    password = Column(String, nullable=False)
    access = Column(Boolean, default=False)
