from typing import List, Optional
from sqlalchemy.orm import Session
from domain.models.activity_schedule import ActivitySchedule
from infrastructure.models.activity_schedule_model import ActivityScheduleModel
from infrastructure.databases.factory_database import FactoryDatabase as db_factory

class ActivityScheduleRepository:
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session

    def add(self, item: ActivitySchedule) -> ActivityScheduleModel:
        try:
            row = ActivityScheduleModel(
                activity_id=item.activity_id,
                location=item.location,
                start_at=item.start_at,
                end_at=item.end_at,
                capacity=item.capacity,
                status=item.status or 'SCHEDULED',
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

    def list(self) -> List[ActivityScheduleModel]:
        return self.session.query(ActivityScheduleModel).all()

    def list_by_activity(self, activity_id: int) -> List[ActivityScheduleModel]:
        return self.session.query(ActivityScheduleModel).filter_by(activity_id=activity_id).all()