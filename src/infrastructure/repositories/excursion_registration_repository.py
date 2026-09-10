from typing import List, Optional
from sqlalchemy.orm import Session
from domain.models.excursion_registration import ExcursionRegistration
from infrastructure.models.excursion_registration_model import ExcursionRegistrationModel
from infrastructure.databases.factory_database import FactoryDatabase as db_factory

class ExcursionRegistrationRepository:
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, item: ExcursionRegistration) -> ExcursionRegistrationModel:
        try:
            row = ExcursionRegistrationModel(
                passenger_id=item.passenger_id,
                excursion_id=item.excursion_id,
                booking_id=item.booking_id,
                status=item.status or 'REGISTERED',
                notes=item.notes,
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

    def list(self) -> List[ExcursionRegistrationModel]:
        return self.session.query(ExcursionRegistrationModel).all()

    def get_by_id(self, item_id: int) -> Optional[ExcursionRegistrationModel]:
        return self.session.query(ExcursionRegistrationModel).filter_by(id=item_id).first()

    def update_status(self, item_id: int, status: str) -> Optional[ExcursionRegistrationModel]:
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
