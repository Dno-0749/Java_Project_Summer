from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from infrastructure.databases.base import Base

class AppointmentModel(Base):
    __tablename__ = 'appointments'
    __table_args__ = {'extend_existing': True}  # Thêm dòng này

    id = Column(Integer, primary_key=True)
    consultant_id = Column(Integer, ForeignKey('consultants.id'))
    user_id = Column(Integer,  ForeignKey('flask_user.id'))
    description = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    url_online = Column(String(255), nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime) 