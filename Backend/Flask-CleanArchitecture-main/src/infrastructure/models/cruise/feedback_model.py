# Feedback Model
# Đánh giá của hành khách cho Activity/ShoreExcursion/Service (dịch vụ tự
# mua). Thiết kế theo target_type + target_id (nullable) + target_name
# (snapshot tên hiển thị) thay vì 3 cột FK riêng, vì "Service" hiện chưa
# có bảng riêng trong hệ thống (chỉ là danh mục tĩnh phía frontend).
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from infrastructure.databases.base import Base


class FeedbackModel(Base):
    __tablename__ = 'cruise_feedbacks'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    passenger_id = Column(Integer, ForeignKey('passengers.id'), nullable=False)
    # 'activity' | 'excursion' | 'service' | 'cruise'
    target_type = Column(String(20), nullable=False)
    target_id = Column(Integer, nullable=True)
    target_name = Column(String(255), nullable=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
