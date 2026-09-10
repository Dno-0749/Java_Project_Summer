from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from infrastructure.databases.base import Base


class ActivityModel(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="Sắp diễn ra")
    capacity = Column(Integer, nullable=False, default=0)
    registered = Column(Integer, nullable=False, default=0)
    price = Column(Integer, nullable=False, default=0)
    activity_type = Column(String(50), nullable=False, default="Miễn phí")
    rating = Column(Float, nullable=False, default=0)
    feedback_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)