# Passenger Model
# Hành khách của 1 chuyến cruise. Liên kết với auth_users (tài khoản đăng nhập)
# và cabin (phòng ở). qr_code / rfid_code dùng để xác thực khi check-in
# và ghi nhận giao dịch trên tàu.
from sqlalchemy import Column, Integer, String, ForeignKey
from infrastructure.databases.base import Base


class PassengerModel(Base):
    __tablename__ = 'passengers'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('auth_users.id'), nullable=True)
    cruise_id = Column(Integer, ForeignKey('cruises.id'), nullable=False)
    cabin_id = Column(Integer, ForeignKey('cabins.id'), nullable=True)
    full_name = Column(String(255), nullable=False)
    qr_code = Column(String(255), unique=True, nullable=True)
    rfid_code = Column(String(255), unique=True, nullable=True)
