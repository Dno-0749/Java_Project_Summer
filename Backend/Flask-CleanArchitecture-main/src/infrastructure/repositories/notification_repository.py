from typing import List, Optional
from infrastructure.databases.factory_database import FactoryDatabase as db_factory
from infrastructure.models.cruise.notification_model import NotificationModel


class NotificationRepository:
    def _new_session(self):
        return db_factory.get_database('POSTGREE').new_session()

    def create(self, data: dict) -> NotificationModel:
        session = self._new_session()
        try:
            n = NotificationModel(**data)
            session.add(n)
            session.commit()
            session.refresh(n)
            return n
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list_for_passenger(self, passenger_id: int, cruise_id: int = None) -> List[NotificationModel]:
        """Lấy thông báo riêng của hành khách này CỘNG VỚI thông báo chung
        của cả cruise (passenger_id NULL) nếu biết cruise_id."""
        session = self._new_session()
        try:
            query = session.query(NotificationModel)
            if cruise_id is not None:
                query = query.filter(
                    (NotificationModel.passenger_id == passenger_id) |
                    ((NotificationModel.passenger_id.is_(None)) & (NotificationModel.cruise_id == cruise_id))
                )
            else:
                query = query.filter_by(passenger_id=passenger_id)
            return query.order_by(NotificationModel.created_at.desc()).all()
        finally:
            session.close()

    def mark_read(self, notification_id: int) -> Optional[NotificationModel]:
        session = self._new_session()
        try:
            n = session.query(NotificationModel).filter_by(id=notification_id).first()
            if not n:
                return None
            n.is_read = True
            session.commit()
            session.refresh(n)
            return n
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
