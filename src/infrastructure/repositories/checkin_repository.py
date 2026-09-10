from typing import List, Optional
from sqlalchemy.orm import Session
from domain.models.checkin import CheckIn
from infrastructure.models.checkin_model import CheckInModel
from infrastructure.databases.factory_database import FactoryDatabase as db_factory

class CheckInRepository:
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, item: CheckIn) -> CheckInModel:
        try:
            row = CheckInModel(
                passenger_id=item.passenger_id,
                booking_id=item.booking_id,
                method=item.method or 'QR',
                code=item.code,
                status=item.status or 'PENDING',
                checked_at=item.checked_at,
            )
            self.session.add(row)
            self.session.commit()
            self.session.refresh(row)
            return row
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def list(self) -> List[CheckInModel]:
        return self.session.query(CheckInModel).all()

    def get_by_id(self, item_id: int) -> Optional[CheckInModel]:
        return self.session.query(CheckInModel).filter_by(id=item_id).first()

    def update_status(self, item_id: int, status: str) -> Optional[CheckInModel]:
        row = self.get_by_id(item_id)
        if not row:
            return None
        try:
            row.status = status
            self.session.commit()
            self.session.refresh(row)
            return row
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.close()
