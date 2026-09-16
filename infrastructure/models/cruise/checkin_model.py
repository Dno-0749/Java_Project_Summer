# Checkin Model
# Ghi log mỗi lần hành khách check-in vào 1 registration (activity/excursion)
# bằng QR code, cruise card, hoặc vòng RFID/NFC
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from infrastructure.databases.base import Base


class CheckinModel(Base):
    __tablename__ = 'checkins'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    registration_id = Column(Integer, ForeignKey('registrations.id'), nullable=False)
    # qr, card, rfid
    method = Column(String(50), nullable=False)
    checked_in_at = Column(DateTime, default=datetime.utcnow)
