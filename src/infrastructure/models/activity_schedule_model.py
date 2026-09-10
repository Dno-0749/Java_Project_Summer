from sqlalchemy import Column, Integer, String, DateTime
from infrastructure.databases.base import Base

class ActivityScheduleModel(Base):
    __tablename__ = 'activity_schedules'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, nullable=False)
    location = Column(String(255), nullable=True)
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    capacity = Column(Integer, nullable=False, default=0)
    status = Column(String(50), nullable=False, default='SCHEDULED')