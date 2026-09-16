from typing import List
from infrastructure.databases.factory_database import FactoryDatabase as db_factory
from infrastructure.models.cruise.feedback_model import FeedbackModel


class FeedbackRepository:
    def _new_session(self):
        return db_factory.get_database('POSTGREE').new_session()

    def create(self, data: dict) -> FeedbackModel:
        session = self._new_session()
        try:
            fb = FeedbackModel(**data)
            session.add(fb)
            session.commit()
            session.refresh(fb)
            return fb
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list_by_passenger(self, passenger_id: int) -> List[FeedbackModel]:
        session = self._new_session()
        try:
            return (
                session.query(FeedbackModel)
                .filter_by(passenger_id=passenger_id)
                .order_by(FeedbackModel.created_at.desc())
                .all()
            )
        finally:
            session.close()

    def list_by_target(self, target_type: str, target_id: int = None) -> List[FeedbackModel]:
        session = self._new_session()
        try:
            query = session.query(FeedbackModel).filter_by(target_type=target_type)
            if target_id is not None:
                query = query.filter_by(target_id=target_id)
            return query.order_by(FeedbackModel.created_at.desc()).all()
        finally:
            session.close()
