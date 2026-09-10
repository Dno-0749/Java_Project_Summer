from typing import List, Optional
from sqlalchemy.orm import Session
from domain.models.tour_provider import TourProvider
from infrastructure.models.tour_provider_model import TourProviderModel
from infrastructure.databases.factory_database import FactoryDatabase as db_factory

class TourProviderRepository:
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, item: TourProvider) -> TourProviderModel:
        try:
            row = TourProviderModel(
                name=item.name,
                contact_phone=item.contact_phone,
                contact_email=item.contact_email,
                address=item.address,
                status=item.status or 'ACTIVE',
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

    def list(self) -> List[TourProviderModel]:
        return self.session.query(TourProviderModel).all()

    def get_by_id(self, item_id: int) -> Optional[TourProviderModel]:
        return self.session.query(TourProviderModel).filter_by(id=item_id).first()