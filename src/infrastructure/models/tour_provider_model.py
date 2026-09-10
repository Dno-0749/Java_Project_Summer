from sqlalchemy import Column, Integer, String
from infrastructure.databases.base import Base

class TourProviderModel(Base):
    __tablename__ = 'tour_providers'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default='ACTIVE')