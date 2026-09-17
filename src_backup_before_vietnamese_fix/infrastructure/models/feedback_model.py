from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from infrastructure.databases.base import Base

class FeedbackModel(Base):
    __tablename__ = 'feedbacks'
    __table_args__ = {'extend_existing': True}  # ThÃªm dÃ²ng nÃ y

    id = Column(Integer, primary_key=True)

    feedback_text = Column(String(255))
    evaluation = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime) 
    course_id = Column(Integer, ForeignKey('courses.id'))
    user_id = Column(Integer, ForeignKey('flask_user.id'))
    
#ORM : Object Relational Mapping
# Ãnh xáº¡ Ä‘á»‘i tÆ°á»£ng trong Python vá»›i báº£ng trong cÆ¡ sá»Ÿ dá»¯ liá»‡u
#Ãnh xáº¡ cÃ¡c thuá»™c tÃ­nh cá»§a lá»›p vá»›i cÃ¡c cá»™t trong báº£ng
#Ãnh xáº¡ cÃ¡c má»‘i quan há»‡ giá»¯a cÃ¡c lá»›p vá»›i cÃ¡c khÃ³a ngoáº¡i trong báº£ng
