# Invoice Model
# Hóa đơn tổng hợp cuối chuyến đi, tạo ra từ toàn bộ transaction đã đối soát
# của 1 OnboardAccount. Bất biến (immutable) sau khi xuất - theo Business
# Rule BR-05 trong SRS.
from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from infrastructure.databases.base import Base


class InvoiceModel(Base):
    __tablename__ = 'invoices'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    onboard_account_id = Column(Integer, ForeignKey('onboard_accounts.id'), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    # issued, adjusted
    status = Column(String(50), nullable=False, default='issued')
    issued_at = Column(DateTime, default=datetime.utcnow)
