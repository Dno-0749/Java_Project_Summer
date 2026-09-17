# Cruise Model
# Đại diện cho 1 chuyến hành trình du thuyền (nhiều ngày)
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime
from infrastructure.databases.base import Base


class CruiseModel(Base):
    __tablename__ = 'cruises'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    # planned, ongoing, completed, cancelled
    status = Column(String(50), nullable=False, default='planned')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
