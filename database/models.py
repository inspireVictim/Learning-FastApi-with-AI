from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index = True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    password = Column(String, nullable=False)
    access = Column(Boolean, default=False)

    payments = relationship("Payments", back_populates="user")

class Payments(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    date_of_payment = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="payments")

