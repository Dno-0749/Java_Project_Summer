from typing import List, Optional
from sqlalchemy.orm import Session
from domain.models.activity_registration import ActivityRegistration
from infrastructure.models.activity_registration_model import ActivityRegistrationModel
from infrastructure.databases.factory_database import FactoryDatabase as db_factory

class ActivityRegistrationRepository:
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, item: ActivityRegistration) -> ActivityRegistrationModel:
        try:
            row = ActivityRegistrationModel(
                passenger_id=item.passenger_id,
                activity_id=item.activity_id,
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

    def list(self) -> List[ActivityRegistrationModel]:
        return self.session.query(ActivityRegistrationModel).all()

    def get_by_id(self, item_id: int) -> Optional[ActivityRegistrationModel]:
        return self.session.query(ActivityRegistrationModel).filter_by(id=item_id).first()

    def update_status(self, item_id: int, status: str) -> Optional[ActivityRegistrationModel]:
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
