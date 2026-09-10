from infrastructure.models.activity_registration_model import ActivityRegistrationModel
from infrastructure.repositories.activity_registration_repository import ActivityRegistrationRepository


class ActivityRegistrationService:

    def __init__(self):
        self.repo = ActivityRegistrationRepository()

    def list(self):
        return self.repo.list()

    def get(self, registration_id):
        return self.repo.get(registration_id)

    def get_by_activity(self, activity_id):
        return self.repo.get_by_activity(activity_id)

    def get_by_passenger(self, passenger_id):
        return self.repo.get_by_passenger(passenger_id)

    def create(self, data):
        registration = ActivityRegistrationModel(
            passenger_id=data["passenger_id"],
            activity_id=data["activity_id"],
            booking_id=data.get("booking_id"),
            status=data.get("status", "REGISTERED"),
            notes=data.get("notes")
        )

        return self.repo.add(registration)

    def update(self, registration_id, data):
        registration = self.repo.get(registration_id)

        if not registration:
            return None

        return self.repo.update(registration, data)

    def delete(self, registration_id):
        registration = self.repo.get(registration_id)

        if not registration:
            return False

        self.repo.delete(registration)
        return True