import uuid
from infrastructure.repositories.passenger_repository import PassengerRepository


class PassengerService:
    def __init__(self, repository: PassengerRepository = None):
        self.repository = repository or PassengerRepository()

    def list_by_cruise(self, cruise_id: int):
        return self.repository.list_by_cruise(cruise_id)

    def get(self, passenger_id: int):
        return self.repository.get_by_id(passenger_id)

    def get_by_code(self, code: str):
        return self.repository.get_by_code(code)

    def create(self, cruise_id: int, full_name: str, cabin_id: int = None):
        # Tự sinh qr_code duy nhất nếu không truyền vào - dùng cho check-in/POS
        qr_code = f"CR-{uuid.uuid4().hex[:8].upper()}"
        return self.repository.create({
            "cruise_id": cruise_id,
            "full_name": full_name,
            "cabin_id": cabin_id,
            "qr_code": qr_code,
        })
