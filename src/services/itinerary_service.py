from infrastructure.repositories.itinerary_repository import ItineraryRepository


class ItineraryService:
    def __init__(self, repository: ItineraryRepository = None):
        self.repository = repository or ItineraryRepository()

    # ---------- Cruise ----------
    def list_cruises(self):
        return self.repository.list_cruises()

    def get_cruise(self, cruise_id: int):
        return self.repository.get_cruise(cruise_id)

    def create_cruise(self, data: dict):
        # Business rule (SRS 3.3.1): ngày kết thúc phải sau ngày bắt đầu
        if data.get("end_date") and data.get("start_date"):
            if data["end_date"] <= data["start_date"]:
                raise ValueError("Ngày kết thúc phải sau ngày bắt đầu")
        return self.repository.add_cruise(data)

    def update_cruise(self, cruise_id: int, data: dict):
        return self.repository.update_cruise(cruise_id, data)

    def delete_cruise(self, cruise_id: int):
        return self.repository.delete_cruise(cruise_id)

    # ---------- Port ----------
    def list_ports(self):
        return self.repository.list_ports()

    def create_port(self, data: dict):
        return self.repository.add_port(data)

    # ---------- CruiseDay ----------
    def list_cruise_days(self, cruise_id: int):
        return self.repository.list_cruise_days(cruise_id)

    def create_cruise_day(self, data: dict):
        # Business rule (SRS 3.3.2): giờ rời bến phải sau giờ cập bến
        arrival = data.get("arrival_time")
        departure = data.get("departure_time")
        if arrival and departure and departure <= arrival:
            raise ValueError("Giờ rời bến phải sau giờ cập bến")
        return self.repository.add_cruise_day(data)

    def update_cruise_day(self, day_id: int, data: dict):
        arrival = data.get("arrival_time")
        departure = data.get("departure_time")
        if arrival and departure and departure <= arrival:
            raise ValueError("Giờ rời bến phải sau giờ cập bến")
        day = self.repository.update_cruise_day(day_id, data)

        # BR-07 (SRS): Mọi thay đổi lịch trình phải kích hoạt thông báo tự
        # động tới hành khách liên quan. Gửi broadcast (passenger_id=None)
        # cho toàn bộ hành khách của cruise này.
        if day:
            try:
                from services.notification_service import NotificationService
                NotificationService().create(
                    title="Cập nhật lịch trình",
                    content=f"Lịch trình ngày {day.day_number} đã được điều phối viên cập nhật.",
                    cruise_id=day.cruise_id,
                    category="itinerary",
                    priority="high",
                )
            except Exception:
                pass  # Không để lỗi gửi thông báo làm hỏng thao tác cập nhật chính

        return day

    # ---------- Cabin ----------
    def list_cabins(self, cruise_id: int):
        return self.repository.list_cabins(cruise_id)

    def create_cabin(self, data: dict):
        return self.repository.add_cabin(data)
