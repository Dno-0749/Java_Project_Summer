# Port Model
# Đại diện cho một điểm dừng / cảng mà tàu ghé qua trong hành trình
from sqlalchemy import Column, Integer, String, Text
from infrastructure.databases.base import Base


class PortModel(Base):
    __tablename__ = 'ports'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
