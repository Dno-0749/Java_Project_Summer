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
        Base.metadata.create_all(
            bind=self.engine
        )
