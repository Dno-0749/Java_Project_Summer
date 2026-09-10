from typing import List, Optional
from sqlalchemy.orm import Session
from domain.models.shore_excursion import ShoreExcursion
from infrastructure.models.shore_excursion_model import ShoreExcursionModel
from infrastructure.databases.factory_database import FactoryDatabase as db_factory

class ShoreExcursionRepository:
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, item: ShoreExcursion) -> ShoreExcursionModel:
        try:
            row = ShoreExcursionModel(
                provider_id=item.provider_id,
                name=item.name,
                port_name=item.port_name,
                description=item.description,
                duration_hours=item.duration_hours,
                capacity=item.capacity,
                fee=item.fee,
                status=item.status or 'OPEN',
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

    def list(self) -> List[ShoreExcursionModel]:
        return self.session.query(ShoreExcursionModel).all()

    def get_by_id(self, item_id: int) -> Optional[ShoreExcursionModel]:
        return self.session.query(ShoreExcursionModel).filter_by(id=item_id).first()

    def update_status(self, item_id: int, status: str) -> Optional[ShoreExcursionModel]:
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