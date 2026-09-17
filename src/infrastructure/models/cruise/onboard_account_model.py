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
    # Hạn mức chi tiêu tối đa (credit limit) - số dư không được âm quá
    # ngưỡng này. Mặc định 20 triệu theo yêu cầu nghiệp vụ.
    credit_limit = Column(Numeric(12, 2), default=20000000)
    # open, settled
    status = Column(String(50), nullable=False, default='open')
