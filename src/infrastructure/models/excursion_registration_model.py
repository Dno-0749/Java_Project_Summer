from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime

from infrastructure.databases.base import Base


class ExcursionRegistrationModel(Base):
    __tablename__ = "excursion_registrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    passenger_id = Column(Integer, nullable=True)
    excursion_id = Column(Integer, nullable=False)
    booking_id = Column(Integer, nullable=True)

    guest_code = Column(String(50), nullable=True)
    passenger_name = Column(String(255), nullable=True)
    room = Column(String(50), nullable=True)

    status = Column(
        String(30),
        nullable=False,
        default="REGISTERED"
    )

    notes = Column(String(500), nullable=True)

    checked_in = Column(
        Boolean,
        nullable=False,
        default=False
    )

    checked_in_at = Column(
        DateTime,
        nullable=True
    )

    registered_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
