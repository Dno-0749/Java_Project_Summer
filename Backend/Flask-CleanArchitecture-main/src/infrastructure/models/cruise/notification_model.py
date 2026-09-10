# Notification Model
# Thông báo gửi tới hành khách (lịch trình thay đổi, hoạt động, giao dịch...)
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from infrastructure.databases.base import Base


class NotificationModel(Base):
    __tablename__ = 'cruise_notifications'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    passenger_id = Column(Integer, ForeignKey('passengers.id'), nullable=True)
    # NULL passenger_id = thông báo chung cho toàn bộ hành khách của cruise
    cruise_id = Column(Integer, ForeignKey('cruises.id'), nullable=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    # itinerary, activity, registration, transaction, general
    category = Column(String(50), nullable=False, default='general')
    priority = Column(String(20), nullable=False, default='normal')  # normal, high
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
