from abc import ABC, abstractmethod
from config import FactoryConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class AbstractDatabase(ABC):
    def __init__(self):
        self.database_uri = FactoryConfig.get_config("development").DATABASE_URI

        if self.database_uri.startswith("postgresql://"):
            self.database_uri = self.database_uri.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1
            )

        self.engine = create_engine(
            self.database_uri,
            pool_pre_ping=True
        )

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        self.session = self.SessionLocal()

    @abstractmethod
    def init_database(self, app):
        pass
