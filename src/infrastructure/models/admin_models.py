from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from infrastructure.databases.base import Base


class ShipModel(Base):
    __tablename__ = "ships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    code = Column(String(80), unique=True, nullable=False)
    status = Column(String(40), nullable=False, default="active")
    capacity = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ShipAreaModel(Base):
    __tablename__ = "ship_areas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    deck = Column(String(80), nullable=True)
    status = Column(String(40), nullable=False, default="active")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdminPolicyModel(Base):
    __tablename__ = "admin_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_key = Column(String(120), unique=True, nullable=False)
    policy_value = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdminDeviceModel(Base):
    __tablename__ = "admin_devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_code = Column(String(120), unique=True, nullable=False)
    device_type = Column(String(40), nullable=False)
    status = Column(String(40), nullable=False, default="active")
    location = Column(String(255), nullable=True)
    assigned_to = Column(String(255), nullable=True)
    last_seen_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_user_id = Column(String(120), nullable=True)
    actor_username = Column(String(120), nullable=True)
    action = Column(String(80), nullable=False)
    resource = Column(String(120), nullable=False)
    resource_id = Column(String(120), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
