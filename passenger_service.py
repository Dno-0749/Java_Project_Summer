from domain.models.passenger import Passenger

class PassengerService:
    def __init__(self, repository):
        self.repository = repository

    def list_passengers(self):
        return self.repository.list()

    def create_passenger(self, full_name, passport_number, nationality=None, phone=None, email=None):
        item = Passenger(
            id=None,
            full_name=full_name,
            passport_number=passport_number,
            nationality=nationality,
            phone=phone,
            email=email,
            status='ACTIVE',
        )
        return self.repository.add(item)

    def update_passenger(self, passenger_id, full_name, passport_number, nationality=None, phone=None, email=None):
        item = Passenger(
            id=passenger_id,
            full_name=full_name,
            passport_number=passport_number,
            nationality=nationality,
            phone=phone,
            email=email,
            status='ACTIVE',
        )
        return self.repository.update(passenger_id, item)
