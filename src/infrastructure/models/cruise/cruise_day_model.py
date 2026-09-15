# CruiseDay Model
# Lịch trình theo từng ngày của 1 cruise, mỗi ngày có thể gắn với 1 cảng (port)
from sqlalchemy import Column, Integer, ForeignKey, Date, Time
from infrastructure.databases.base import Base


class CruiseDayModel(Base):
    __tablename__ = 'cruise_days'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cruise_id = Column(Integer, ForeignKey('cruises.id'), nullable=False)
    day_number = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    port_id = Column(Integer, ForeignKey('ports.id'), nullable=True)
    arrival_time = Column(Time, nullable=True)
    departure_time = Column(Time, nullable=True)
