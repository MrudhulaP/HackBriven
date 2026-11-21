import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100), nullable=False)
    mobile = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    preferred_language = Column(String(10), default="hi", nullable=False)  # hi, kn, en
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    shops = relationship("Shop", back_populates="owner", cascade="all, delete-orphan")


class Shop(Base):
    __tablename__ = "shops"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    shop_name = Column(String(150), nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="shops")
    customers = relationship("Customer", back_populates="shop", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="shop", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="shop", cascade="all, delete-orphan")
