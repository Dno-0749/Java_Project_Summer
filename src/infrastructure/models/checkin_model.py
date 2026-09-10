from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from infrastructure.databases.base import Base

class CheckInModel(Base):
    __tablename__ = 'checkins'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey('passengers.id'), nullable=False)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=True)
    method = Column(String(50), nullable=False, default='QR')
    code = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default='PENDING')
    checked_at = Column(DateTime, nullable=True)
