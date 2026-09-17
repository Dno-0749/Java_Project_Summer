from typing import List, Optional
from infrastructure.databases.factory_database import FactoryDatabase as db_factory
from infrastructure.models.cruise.booking_model import BookingModel


class BookingRepository:
    def _new_session(self):
        return db_factory.get_database('POSTGREE').new_session()

    def list_bookings(self) -> List[BookingModel]:
        session = self._new_session()
        try:
            return session.query(BookingModel).order_by(BookingModel.created_at.desc()).all()
        finally:
            session.close()

    def get_booking(self, booking_id: int) -> Optional[BookingModel]:
        session = self._new_session()
        try:
            return session.query(BookingModel).filter_by(id=booking_id).first()
        finally:
            session.close()

    def create_booking(self, data: dict) -> BookingModel:
        session = self._new_session()
        try:
            booking = BookingModel(**data)
            session.add(booking)
            session.commit()
            session.refresh(booking)
            return booking
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_booking(self, booking_id: int, data: dict) -> Optional[BookingModel]:
        session = self._new_session()
        try:
            booking = session.query(BookingModel).filter_by(id=booking_id).first()
            if not booking:
                return None
            for key, value in data.items():
                setattr(booking, key, value)
            session.commit()
            session.refresh(booking)
            return booking
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_status(self, booking_id: int, status: str) -> Optional[BookingModel]:
        return self.update_booking(booking_id, {"status": status})

    def delete_booking(self, booking_id: int) -> bool:
        session = self._new_session()
        try:
            booking = session.query(BookingModel).filter_by(id=booking_id).first()
            if not booking:
                return False
            session.delete(booking)
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
