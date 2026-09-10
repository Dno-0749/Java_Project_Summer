# Transaction Model
# Giao dịch chi tiêu trên tàu (POS). local_id là id được sinh ở THIẾT BỊ
# (POS/tablet) khi ghi offline -> dùng unique constraint để chống ghi trùng
# khi thiết bị đồng bộ lại sau khi có mạng.
#
# sync_status:
#   pending_sync -> giao dịch mới nhận từ thiết bị offline, chưa đối soát
#   synced       -> đã đồng bộ lên server bình thường (online ngay lúc tạo)
#   reconciled   -> đã được bộ phận Finance đối soát ở cuối chuyến
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from infrastructure.databases.base import Base


class TransactionModel(Base):
    __tablename__ = 'onboard_transactions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    local_id = Column(String(100), unique=True, nullable=True)
    onboard_account_id = Column(Integer, ForeignKey('onboard_accounts.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('auth_users.id'), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(255), nullable=True)
    sync_status = Column(String(50), nullable=False, default='synced')
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime, nullable=True)
