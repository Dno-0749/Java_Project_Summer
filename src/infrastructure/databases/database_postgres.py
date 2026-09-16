

from infrastructure.databases.abstract_database import AbstractDatabase
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config, DevelopmentConfig
from infrastructure.databases.base import Base

class DatabasePostgres(AbstractDatabase):
    def __innit__(self):
        super().__init__()
        
    def init_database(self, app):
        Base.metadata.create_all(bind=self.engine)
        with self.engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE bookings ALTER COLUMN cruise_id DROP NOT NULL"
            )
            connection.exec_driver_sql(
                "ALTER TABLE bookings ALTER COLUMN booking_reference DROP NOT NULL"
            )
            connection.exec_driver_sql(
                "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS ship_name VARCHAR(255)"
            )
            connection.exec_driver_sql(
                "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS customer_name VARCHAR(255)"
            )
            connection.exec_driver_sql(
                "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS start_date DATE"
            )
            connection.exec_driver_sql(
                "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS end_date DATE"
            )
            connection.exec_driver_sql(
                "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP"
            )