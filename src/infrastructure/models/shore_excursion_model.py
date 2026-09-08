from sqlalchemy import Column, Integer, String, Float
from infrastructure.databases.base import Base

class ShoreExcursionModel(Base):
    __tablename__ = 'shore_excursions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    port_name = Column(String(255), nullable=True)
    description = Column(String(500), nullable=True)
    duration_hours = Column(Float, nullable=True)
    capacity = Column(Integer, nullable=False, default=0)
    fee = Column(Float, nullable=False, default=0)
    status = Column(String(50), nullable=False, default='OPEN')