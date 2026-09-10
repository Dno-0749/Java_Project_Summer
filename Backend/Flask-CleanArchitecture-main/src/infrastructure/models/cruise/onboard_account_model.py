# OnboardAccount Model
# Tài khoản chi tiêu (cashless) của mỗi hành khách trong suốt chuyến đi.
# balance được cập nhật mỗi khi có transaction mới (xem transaction_model.py)
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from infrastructure.databases.base import Base


class OnboardAccountModel(Base):
    __tablename__ = 'onboard_accounts'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    passenger_id = Column(Integer, ForeignKey('passengers.id'), unique=True, nullable=False)
    balance = Column(Numeric(12, 2), default=0)
    # open, settled
    status = Column(String(50), nullable=False, default='open')
