from typing import List, Optional

from sqlalchemy.orm import Session

from domain.models.shore_excursion import ShoreExcursion
from infrastructure.models.shore_excursion_model import ShoreExcursionModel
from infrastructure.databases.factory_database import FactoryDatabase as db_factory


class ShoreExcursionRepository:

    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database("POSTGREE").session

    def add(self, item: ShoreExcursion) -> ShoreExcursionModel:
        try:
            row = ShoreExcursionModel(
                provider_id=item.provider_id,
                name=item.name,
                date=item.date,
                time=item.time,
                location=item.location,
                port_name=item.location,
                description=item.description,
                duration_hours=item.duration_hours,
                capacity=item.capacity,
                registered=item.registered,
                fee=item.price,
                rating=0,
                feedback_count=0,
                status=item.status or "OPEN"
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
        try:
            return self.session.query(
                ShoreExcursionModel
            ).all()
        finally:
            self.session.close()

    def get_by_id(
        self,
        item_id: int
    ) -> Optional[ShoreExcursionModel]:
        try:
            return self.session.query(
                ShoreExcursionModel
            ).filter_by(id=item_id).first()
        finally:
            self.session.close()

    def update(
        self,
        item_id: int,
        data: dict
    ) -> Optional[ShoreExcursionModel]:

        try:
            row = self.session.query(
                ShoreExcursionModel
            ).filter_by(id=item_id).first()

            if not row:
                return None

            for key, value in data.items():
                if hasattr(row, key):
                    setattr(row, key, value)

            self.session.commit()
            self.session.refresh(row)

            return row

        except Exception:
            self.session.rollback()
            raise

        finally:
            self.session.close()

    def update_status(
        self,
        item_id: int,
        status: str
    ) -> Optional[ShoreExcursionModel]:

        try:
            row = self.session.query(
                ShoreExcursionModel
            ).filter_by(id=item_id).first()

            if not row:
                return None

            row.status = status

            self.session.commit()
            self.session.refresh(row)

            return row

        except Exception:
            self.session.rollback()
            raise

        finally:
            self.session.close()
