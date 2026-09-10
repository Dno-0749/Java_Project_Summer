from typing import Optional
from infrastructure.databases.factory_database import FactoryDatabase as db_factory
from infrastructure.models.cruise.checkin_model import CheckinModel
from infrastructure.models.cruise.registration_model import RegistrationModel


class CheckinRepository:
    def _new_session(self):
        return db_factory.get_database('POSTGREE').new_session()

    def get_registration(self, registration_id: int) -> Optional[RegistrationModel]:
        session = self._new_session()
        try:
            return session.query(RegistrationModel).filter_by(id=registration_id).first()
        finally:
            session.close()

    def get_existing_checkin(self, registration_id: int) -> Optional[CheckinModel]:
        session = self._new_session()
        try:
            return session.query(CheckinModel).filter_by(registration_id=registration_id).first()
        finally:
            session.close()

    def add_checkin(self, registration_id: int, method: str) -> CheckinModel:
        session = self._new_session()
        try:
            checkin = CheckinModel(registration_id=registration_id, method=method)
            session.add(checkin)

            registration = session.query(RegistrationModel).filter_by(id=registration_id).first()
            if registration:
                registration.status = "checked_in"

            session.commit()
            session.refresh(checkin)
            return checkin
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
