# Cabin Model
# Phòng/cabin trên tàu, thuộc về 1 cruise cụ thể
from sqlalchemy import Column, Integer, String, ForeignKey
from infrastructure.databases.base import Base


class CabinModel(Base):
    __tablename__ = 'cabins'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cruise_id = Column(Integer, ForeignKey('cruises.id'), nullable=False)
    cabin_number = Column(String(50), nullable=False)
