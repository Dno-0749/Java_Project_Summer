# ShoreExcursion Model
# Tour trên bờ tại mỗi điểm dừng (cruise_day), do nhà cung cấp địa phương tổ chức
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from infrastructure.databases.base import Base


class ShoreExcursionModel(Base):
    __tablename__ = 'shore_excursions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    cruise_day_id = Column(Integer, ForeignKey('cruise_days.id'), nullable=False)
    name = Column(String(255), nullable=False)
    provider_name = Column(String(255), nullable=True)
    gathering_time = Column(DateTime, nullable=True)
    return_time = Column(DateTime, nullable=True)
    capacity = Column(Integer, nullable=True)
    price = Column(Numeric(10, 2), default=0)
    # scheduled, completed, cancelled, delayed
    status = Column(String(50), nullable=False, default='scheduled')
