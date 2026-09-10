from infrastructure.databases.factory_database import FactoryDatabase
from infrastructure.models.activity_model import ActivityModel


class ActivityRepository:

    def __init__(self):
        self.session = FactoryDatabase.get_database("POSTGREE").SessionLocal()

    def list(self):
        return self.session.query(ActivityModel).all()

    def get(self, activity_id):
        return (
            self.session
            .query(ActivityModel)
            .filter_by(id=activity_id)
            .first()
        )

    def add(self, activity):
        self.session.add(activity)
        self.session.commit()
        self.session.refresh(activity)
        return activity

    def update(self, activity, data):
        for key, value in data.items():
            setattr(activity, key, value)

        self.session.commit()
        self.session.refresh(activity)
        return activity

    def delete(self, activity):
        self.session.delete(activity)
        self.session.commit()