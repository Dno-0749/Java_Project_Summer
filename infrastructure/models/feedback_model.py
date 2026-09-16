from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from infrastructure.databases.base import Base

class FeedbackModel(Base):
    __tablename__ = 'feedbacks'
    __table_args__ = {'extend_existing': True}  # Thêm dòng này

    id = Column(Integer, primary_key=True)

    feedback_text = Column(String(255))
    evaluation = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime) 
    course_id = Column(Integer, ForeignKey('courses.id'))
    user_id = Column(Integer, ForeignKey('flask_user.id'))
    
#ORM : Object Relational Mapping
# Ánh xạ đối tượng trong Python với bảng trong cơ sở dữ liệu
#Ánh xạ các thuộc tính của lớp với các cột trong bảng
#Ánh xạ các mối quan hệ giữa các lớp với các khóa ngoại trong bảng