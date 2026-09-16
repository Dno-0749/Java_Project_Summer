from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, String

from infrastructure.databases.base import Base


class BookingModel(Base):
    __tablename__ = "bookings"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Legacy booking columns remain mapped so existing Supabase rows are safe.
    cruise_id = Column(Integer, nullable=True)
    cabin_id = Column(Integer, nullable=True)
    booking_reference = Column(String(100), nullable=True)
    ship_name = Column(String(255), nullable=True)
    customer_name = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String(30), nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)