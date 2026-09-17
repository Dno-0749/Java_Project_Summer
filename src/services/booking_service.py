from datetime import datetime
from infrastructure.repositories.booking_repository import BookingRepository

VALID_STATUSES = ["pending", "confirmed", "cancelled", "completed"]


def _parse_dates(data: dict) -> dict:
    """Chuyển start_date/end_date từ chuỗi 'YYYY-MM-DD' (JSON) sang Python
    date - SQLAlchemy Date column không tự chuyển đổi chuỗi."""
    data = dict(data)
    for key in ("start_date", "end_date"):
        value = data.get(key)
        if isinstance(value, str) and value:
            data[key] = datetime.strptime(value, "%Y-%m-%d").date()
    return data


class BookingService:
    def __init__(self, repository: BookingRepository = None):
        self.repository = repository or BookingRepository()

    def list_bookings(self):
        return self.repository.list_bookings()

    def get_booking(self, booking_id: int):
        return self.repository.get_booking(booking_id)

    def create_booking(self, data: dict):
        if data.get("status") and data["status"] not in VALID_STATUSES:
            raise ValueError(f"Trạng thái không hợp lệ. Chỉ chấp nhận: {VALID_STATUSES}")
        return self.repository.create_booking(_parse_dates(data))

    def update_booking(self, booking_id: int, data: dict):
        if data.get("status") and data["status"] not in VALID_STATUSES:
            raise ValueError(f"Trạng thái không hợp lệ. Chỉ chấp nhận: {VALID_STATUSES}")
        return self.repository.update_booking(booking_id, _parse_dates(data))

    def update_status(self, booking_id: int, status: str):
        if status not in VALID_STATUSES:
            raise ValueError(f"Trạng thái không hợp lệ. Chỉ chấp nhận: {VALID_STATUSES}")
        return self.repository.update_status(booking_id, status)

    def delete_booking(self, booking_id: int):
        return self.repository.delete_booking(booking_id)
