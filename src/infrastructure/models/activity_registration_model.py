from sqlalchemy import Column, Integer, String, ForeignKey
from infrastructure.databases.base import Base

class ActivityRegistrationModel(Base):
    __tablename__ = 'activity_registrations'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    passenger_id = Column(Integer, ForeignKey('passengers.id'), nullable=False)
    activity_id = Column(Integer, nullable=False)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=True)
    status = Column(String(50), nullable=False, default='REGISTERED')
    notes = Column(String(255), nullable=True)
