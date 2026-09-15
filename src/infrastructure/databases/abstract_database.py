from abc import ABC, abstractmethod
import psycopg2
from psycopg2 import sql
# from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from config import DevelopmentConfig,Config, FactoryConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
class AbstractDatabase(ABC):
    def __init__(self):
        env = os.environ.get('FLASK_ENV', 'development')
        self.database_uri = FactoryConfig.get_config(env).DATABASE_URI
        # QUAN TRỌNG: create_engine() chỉ chạy 1 LẦN nhờ FactoryDatabase là
        # singleton (xem factory_database.py). pool_size/max_overflow được
        # giới hạn thấp để tổng kết nối không vượt quá giới hạn pooler của
        # Supabase (mặc định 15 với gói free, session mode - cổng 5432).
        # pool_pre_ping tránh lỗi dùng phải connection đã bị Supabase đóng
        # do idle timeout; pool_recycle chủ động tái tạo kết nối cũ.
        self.engine = create_engine(
            self.database_uri,
            pool_size=5,
            max_overflow=5,
            pool_pre_ping=True,
            pool_recycle=1800,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.SessionLocal()

    def new_session(self):
        """Trả về 1 Session MỚI (nhẹ, rẻ) nhưng dùng chung 1 Engine/pool đã
        tạo sẵn - KHÔNG tạo engine/connection pool mới. Đây là cách đúng để
        mỗi thao tác CRUD có 1 session riêng (tránh lỗi 'detached instance')
        mà không làm tràn giới hạn kết nối tới Supabase."""
        return self.SessionLocal()

    @abstractmethod
    def init_database(app):
        pass