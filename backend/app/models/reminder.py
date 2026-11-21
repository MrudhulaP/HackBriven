import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    shop_id = Column(String(36), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="DRAFT", nullable=False)  # 'DRAFT', 'SENT', 'SHARED'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    shop = relationship("Shop", back_populates="reminders")
    customer = relationship("Customer", back_populates="reminders")
