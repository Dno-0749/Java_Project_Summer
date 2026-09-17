from typing import List, Optional
from infrastructure.databases.factory_database import FactoryDatabase as db_factory
from infrastructure.models.cruise.activity_model import ActivityModel
from infrastructure.models.cruise.shore_excursion_model import ShoreExcursionModel
from infrastructure.models.cruise.registration_model import RegistrationModel


class ActivityRepository:
    def _new_session(self):
        return db_factory.get_database('POSTGREE').new_session()

    # ---------- Activity ----------
    def list_activities(self, cruise_id: int) -> List[ActivityModel]:
        session = self._new_session()
        try:
            return session.query(ActivityModel).filter_by(cruise_id=cruise_id).all()
        finally:
            session.close()

    def get_activity(self, activity_id: int) -> Optional[ActivityModel]:
        session = self._new_session()
        try:
            return session.query(ActivityModel).filter_by(id=activity_id).first()
        finally:
            session.close()

    def add_activity(self, data: dict) -> ActivityModel:
        session = self._new_session()
        try:
            activity = ActivityModel(**data)
            session.add(activity)
            session.commit()
            session.refresh(activity)
            return activity
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ---------- ShoreExcursion ----------
    def list_excursions(self, cruise_day_id: int) -> List[ShoreExcursionModel]:
        session = self._new_session()
        try:
            return session.query(ShoreExcursionModel).filter_by(cruise_day_id=cruise_day_id).all()
        finally:
            session.close()

    def get_excursion(self, excursion_id: int) -> Optional[ShoreExcursionModel]:
        session = self._new_session()
        try:
            return session.query(ShoreExcursionModel).filter_by(id=excursion_id).first()
        finally:
            session.close()

    def add_excursion(self, data: dict) -> ShoreExcursionModel:
        session = self._new_session()
        try:
            excursion = ShoreExcursionModel(**data)
            session.add(excursion)
            session.commit()
            session.refresh(excursion)
            return excursion
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_excursion_status(self, excursion_id: int, status: str) -> Optional[ShoreExcursionModel]:
        session = self._new_session()
        try:
            excursion = session.query(ShoreExcursionModel).filter_by(id=excursion_id).first()
            if not excursion:
                return None
            excursion.status = status
            session.commit()
            session.refresh(excursion)
            return excursion
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ---------- Registration ----------
    def count_registrations(self, activity_id: int = None, excursion_id: int = None) -> int:
        session = self._new_session()
        try:
            query = session.query(RegistrationModel).filter(
                RegistrationModel.status.in_(["registered", "checked_in"])
            )
            if activity_id:
                query = query.filter_by(activity_id=activity_id)
            if excursion_id:
                query = query.filter_by(excursion_id=excursion_id)
            return query.count()
        finally:
            session.close()

    def list_registrations(self, activity_id: int = None, excursion_id: int = None, passenger_id: int = None) -> List[RegistrationModel]:
        session = self._new_session()
        try:
            query = session.query(RegistrationModel)
            if activity_id:
                query = query.filter_by(activity_id=activity_id)
            if excursion_id:
                query = query.filter_by(excursion_id=excursion_id)
            if passenger_id:
                query = query.filter_by(passenger_id=passenger_id)
            return query.all()
        finally:
            session.close()

    def get_registration(self, registration_id: int) -> Optional[RegistrationModel]:
        session = self._new_session()
        try:
            return session.query(RegistrationModel).filter_by(id=registration_id).first()
        finally:
            session.close()

    def add_registration(self, data: dict) -> RegistrationModel:
        session = self._new_session()
        try:
            registration = RegistrationModel(**data)
            session.add(registration)
            session.commit()
            session.refresh(registration)
            return registration
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_registration_status(self, registration_id: int, status: str) -> Optional[RegistrationModel]:
        session = self._new_session()
        try:
            reg = session.query(RegistrationModel).filter_by(id=registration_id).first()
            if not reg:
                return None
            reg.status = status
            session.commit()
            session.refresh(reg)
            return reg
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
