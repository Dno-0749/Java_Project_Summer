# Registration Model
# Đăng ký của hành khách cho 1 activity HOẶC 1 shore excursion.
# Dùng chung 1 bảng, chỉ 1 trong 2 cột activity_id / excursion_id được điền.
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from infrastructure.databases.base import Base


class RegistrationModel(Base):
    __tablename__ = 'registrations'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    passenger_id = Column(Integer, ForeignKey('passengers.id'), nullable=False)
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=True)
    excursion_id = Column(Integer, ForeignKey('shore_excursions.id'), nullable=True)
    # registered, checked_in, cancelled, no_show
    status = Column(String(50), nullable=False, default='registered')
    registered_at = Column(DateTime, default=datetime.utcnow)
