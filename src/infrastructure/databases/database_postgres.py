from infrastructure.databases.abstract_database import AbstractDatabase
from infrastructure.databases.base import Base

from infrastructure.models.activity_model import ActivityModel
from infrastructure.models.activity_registration_model import ActivityRegistrationModel
from infrastructure.models.activity_schedule_model import ActivityScheduleModel
from infrastructure.models.shore_excursion_model import ShoreExcursionModel
from infrastructure.models.tour_provider_model import TourProviderModel
from infrastructure.models.excursion_registration_model import ExcursionRegistrationModel

class DatabasePostgres(AbstractDatabase):
    def __init__(self):
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
            schema_updates = (
                "ALTER TABLE ships ADD COLUMN IF NOT EXISTS status VARCHAR(40) DEFAULT 'active'",
                "ALTER TABLE ships ADD COLUMN IF NOT EXISTS capacity INTEGER",
                "ALTER TABLE ships ADD COLUMN IF NOT EXISTS description TEXT",
                "ALTER TABLE ships ADD COLUMN IF NOT EXISTS created_at TIMESTAMP",
                "ALTER TABLE ships ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP",
                "ALTER TABLE ship_areas ADD COLUMN IF NOT EXISTS deck VARCHAR(80)",
                "ALTER TABLE ship_areas ADD COLUMN IF NOT EXISTS status VARCHAR(40) DEFAULT 'active'",
                "ALTER TABLE ship_areas ADD COLUMN IF NOT EXISTS description TEXT",
                "ALTER TABLE ship_areas ADD COLUMN IF NOT EXISTS created_at TIMESTAMP",
                "ALTER TABLE ship_areas ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP",
                "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS actor_user_id VARCHAR(120)",
                "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS actor_username VARCHAR(120)",
                "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS action VARCHAR(80)",
                "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS resource VARCHAR(120)",
                "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS resource_id VARCHAR(120)",
                "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS details TEXT",
                "ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS created_at TIMESTAMP",
                "ALTER TABLE activities ADD COLUMN IF NOT EXISTS cruise_id INTEGER",
                "ALTER TABLE activities ADD COLUMN IF NOT EXISTS start_time TIMESTAMP",
                "ALTER TABLE activities ADD COLUMN IF NOT EXISTS end_time TIMESTAMP",
                "ALTER TABLE activities ADD COLUMN IF NOT EXISTS fee NUMERIC(10, 2) DEFAULT 0",
                "ALTER TABLE activities ADD COLUMN IF NOT EXISTS is_included_in_package BOOLEAN DEFAULT FALSE",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS provider_id INTEGER",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS date DATE",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS time TIME",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS location VARCHAR(255)",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS port_name VARCHAR(255)",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS description TEXT",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS duration_hours INTEGER",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS registered INTEGER DEFAULT 0",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS fee NUMERIC(10, 2) DEFAULT 0",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS rating NUMERIC(3, 2) DEFAULT 0",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS feedback_count INTEGER DEFAULT 0",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS cruise_day_id INTEGER",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS provider_name VARCHAR(255)",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS gathering_time TIMESTAMP",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS return_time TIMESTAMP",
                "ALTER TABLE shore_excursions ADD COLUMN IF NOT EXISTS price NUMERIC(10, 2) DEFAULT 0",
                "ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255)",
                "ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS status VARCHAR(40) DEFAULT 'Active'",
                "ALTER TABLE auth_users ADD COLUMN IF NOT EXISTS passenger_id INTEGER",
            )
            for statement in schema_updates:
                connection.exec_driver_sql(statement)
