from infrastructure.databases.factory_database import FactoryDatabase
from infrastructure.models.activity_registration_model import ActivityRegistrationModel


class ActivityRegistrationRepository:

    def __init__(self):
        self.session = FactoryDatabase.get_database("POSTGREE").SessionLocal()

    def list(self):
        return self.session.query(ActivityRegistrationModel).all()

    def get(self, registration_id):
        return (
            self.session
            .query(ActivityRegistrationModel)
            .filter_by(id=registration_id)
            .first()
        )

    def get_by_activity(self, activity_id):
        return (
            self.session
            .query(ActivityRegistrationModel)
            .filter_by(activity_id=activity_id)
            .all()
        )

    def get_by_passenger(self, passenger_id):
        return (
            self.session
            .query(ActivityRegistrationModel)
            .filter_by(passenger_id=passenger_id)
            .all()
        )

    def add(self, registration):
        self.session.add(registration)
        self.session.commit()
        self.session.refresh(registration)
        return registration

    def update(self, registration, data):
        for key, value in data.items():
            setattr(registration, key, value)

        self.session.commit()
        self.session.refresh(registration)
        return registration

    def delete(self, registration):
        self.session.delete(registration)
        self.session.commit()