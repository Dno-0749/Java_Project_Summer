from typing import List, Optional
from uuid import uuid4
from infrastructure.databases.factory_database import FactoryDatabase as db_factory
from infrastructure.models.cruise.cruise_model import CruiseModel
from infrastructure.models.cruise.port_model import PortModel
from infrastructure.models.cruise.cruise_day_model import CruiseDayModel
from infrastructure.models.cruise.cabin_model import CabinModel
from infrastructure.models.cruise.booking_model import BookingModel


class ItineraryRepository:
    """Repository dùng chung cho nhóm Lịch trình: Cruise, Port, CruiseDay, Cabin.
    Mỗi hàm tự lấy 1 session RIÊNG qua _new_session() (dùng chung 1
    Engine/pool đã tạo sẵn - KHÔNG tạo engine mới) để tránh vừa lỗi
    'detached instance' vừa tràn giới hạn connection pool của Supabase.
    """

    def _new_session(self):
        return db_factory.get_database('POSTGREE').new_session()

    # ---------- Cruise ----------
    def list_cruises(self) -> List[CruiseModel]:
        session = self._new_session()
        try:
            return session.query(CruiseModel).order_by(CruiseModel.start_date).all()
        finally:
            session.close()

    def get_cruise(self, cruise_id: int) -> Optional[CruiseModel]:
        session = self._new_session()
        try:
            return session.query(CruiseModel).filter_by(id=cruise_id).first()
        finally:
            session.close()

    def add_cruise(self, data: dict) -> CruiseModel:
        session = self._new_session()
        try:
            cruise = CruiseModel(**data)
            session.add(cruise)
            session.commit()
            session.refresh(cruise)
            return cruise
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_cruise(self, cruise_id: int, data: dict) -> Optional[CruiseModel]:
        session = self._new_session()
        try:
            cruise = session.query(CruiseModel).filter_by(id=cruise_id).first()
            if not cruise:
                return None
            for key, value in data.items():
                setattr(cruise, key, value)
            session.commit()
            session.refresh(cruise)
            return cruise
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_cruise(self, cruise_id: int) -> bool:
        session = self._new_session()
        try:
            cruise = session.query(CruiseModel).filter_by(id=cruise_id).first()
            if not cruise:
                return False
            session.delete(cruise)
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ---------- Port ----------
    def list_ports(self) -> List[PortModel]:
        session = self._new_session()
        try:
            return session.query(PortModel).all()
        finally:
            session.close()

    def add_port(self, data: dict) -> PortModel:
        session = self._new_session()
        try:
            port = PortModel(**data)
            session.add(port)
            session.commit()
            session.refresh(port)
            return port
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ---------- CruiseDay ----------
    def list_cruise_days(self, cruise_id: int) -> List[CruiseDayModel]:
        session = self._new_session()
        try:
            return (
                session.query(CruiseDayModel)
                .filter_by(cruise_id=cruise_id)
                .order_by(CruiseDayModel.day_number)
                .all()
            )
        finally:
            session.close()

    def add_cruise_day(self, data: dict) -> CruiseDayModel:
        session = self._new_session()
        try:
            day = CruiseDayModel(**data)
            session.add(day)
            session.commit()
            session.refresh(day)
            return day
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_cruise_day(self, day_id: int, data: dict) -> Optional[CruiseDayModel]:
        session = self._new_session()
        try:
            day = session.query(CruiseDayModel).filter_by(id=day_id).first()
            if not day:
                return None
            for key, value in data.items():
                setattr(day, key, value)
            session.commit()
            session.refresh(day)
            return day
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ---------- Cabin ----------
    def list_cabins(self, cruise_id: int) -> List[CabinModel]:
        session = self._new_session()
        try:
            return session.query(CabinModel).filter_by(cruise_id=cruise_id).all()
        finally:
            session.close()

    def add_cabin(self, data: dict) -> CabinModel:
        session = self._new_session()
        try:
            cabin = CabinModel(**data)
            session.add(cabin)
            session.commit()
            session.refresh(cabin)
            return cabin
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ---------- Booking ----------
    def list_bookings(self) -> List[BookingModel]:
        session = self._new_session()
        try:
            return session.query(BookingModel).order_by(BookingModel.start_date).all()
        finally:
            session.close()

    def get_booking(self, booking_id: int) -> Optional[BookingModel]:
        session = self._new_session()
        try:
            return session.query(BookingModel).filter_by(id=booking_id).first()
        finally:
            session.close()

    def find_ship_overlap(self, ship_name: str, start_date, end_date, exclude_id=None):
        session = self._new_session()
        try:
            query = session.query(BookingModel).filter(
                BookingModel.ship_name == ship_name,
                BookingModel.status != "cancelled",
                BookingModel.start_date <= end_date,
                BookingModel.end_date >= start_date,
            )
            if exclude_id is not None:
                query = query.filter(BookingModel.id != exclude_id)
            return query.first()
        finally:
            session.close()

    def add_booking(self, data: dict) -> BookingModel:
        session = self._new_session()
        try:
            data = {
                **data,
                "booking_reference": f"WEB-{uuid4().hex[:10].upper()}",
            }
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

    def update_booking_status(self, booking_id: int, status: str) -> Optional[BookingModel]:
        session = self._new_session()
        try:
            booking = session.query(BookingModel).filter_by(id=booking_id).first()
            if not booking:
                return None
            booking.status = status
            session.commit()
            session.refresh(booking)
            return booking
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

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
