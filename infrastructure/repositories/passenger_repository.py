from typing import List, Optional
from infrastructure.databases.factory_database import FactoryDatabase as db_factory
from infrastructure.models.cruise.passenger_model import PassengerModel


class PassengerRepository:
    def _new_session(self):
        return db_factory.get_database('POSTGREE').new_session()

    def list_by_cruise(self, cruise_id: int) -> List[PassengerModel]:
        session = self._new_session()
        try:
            return session.query(PassengerModel).filter_by(cruise_id=cruise_id).all()
        finally:
            session.close()

    def get_by_id(self, passenger_id: int) -> Optional[PassengerModel]:
        session = self._new_session()
        try:
            return session.query(PassengerModel).filter_by(id=passenger_id).first()
        finally:
            session.close()

    def get_by_code(self, code: str) -> Optional[PassengerModel]:
        """Tìm hành khách theo qr_code HOẶC rfid_code - dùng cho bước xác thực tại POS."""
        session = self._new_session()
        try:
            return (
                session.query(PassengerModel)
                .filter((PassengerModel.qr_code == code) | (PassengerModel.rfid_code == code))
                .first()
            )
        finally:
            session.close()

    def create(self, data: dict) -> PassengerModel:
        session = self._new_session()
        try:
            passenger = PassengerModel(**data)
            session.add(passenger)
            session.commit()
            session.refresh(passenger)
            return passenger
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
