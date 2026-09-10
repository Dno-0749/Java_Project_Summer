from infrastructure.databases.abstract_database import AbstractDatabase
from infrastructure.databases.base import Base

# Import tất cả model để SQLAlchemy biết các bảng cần tạo
from infrastructure.models.activity_model import ActivityModel
from infrastructure.models.activity_registration_model import ActivityRegistrationModel


class DatabasePostgres(AbstractDatabase):

    def __init__(self):
        super().__init__()

    def init_database(self, app):
        Base.metadata.create_all(bind=self.engine)