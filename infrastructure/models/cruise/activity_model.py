# Activity Model
# Hoạt động giải trí / dịch vụ trên tàu (ví dụ: lớp yoga, buffet, spa...)
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey
from infrastructure.databases.base import Base


class ActivityModel(Base):
    __tablename__ = 'activities'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cruise_id = Column(Integer, ForeignKey('cruises.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    capacity = Column(Integer, nullable=True)
    fee = Column(Numeric(10, 2), default=0)
    is_included_in_package = Column(Boolean, default=False)
