from infrastructure.repositories.activity_repository import ActivityRepository


class ActivityService:
    def __init__(self, repository: ActivityRepository = None):
        self.repository = repository or ActivityRepository()

    # ---------- Activity ----------
    def list_activities(self, cruise_id: int):
        return self.repository.list_activities(cruise_id)

    def get_activity(self, activity_id: int):
        return self.repository.get_activity(activity_id)

    def create_activity(self, data: dict):
        if data.get("capacity") is not None and data["capacity"] <= 0:
            raise ValueError("Sức chứa phải lớn hơn 0")
        return self.repository.add_activity(data)

    # ---------- ShoreExcursion ----------
    def list_excursions(self, cruise_day_id: int):
        return self.repository.list_excursions(cruise_day_id)

    def get_excursion(self, excursion_id: int):
        return self.repository.get_excursion(excursion_id)

    def create_excursion(self, data: dict):
        # Business Rule BR-03 (SRS): giờ quay lại tàu phải trước giờ tàu rời bến tối thiểu 30 phút.
        # Ở tầng service này chỉ validate "return_time < gathering_time là vô lý", còn việc so
        # sánh chính xác với giờ rời bến của CruiseDay nên thực hiện ở lớp gọi kết hợp (controller
        # gọi cả itinerary_service) - ghi chú TODO để đội dev tiếp tục hoàn thiện.
        gathering = data.get("gathering_time")
        return_time = data.get("return_time")
        if gathering and return_time and return_time <= gathering:
            raise ValueError("Giờ quay lại tàu phải sau giờ tập trung")
        return self.repository.add_excursion(data)

    def update_excursion_status(self, excursion_id: int, status: str):
        valid_statuses = ["scheduled", "completed", "cancelled", "delayed"]
        if status not in valid_statuses:
            raise ValueError(f"Trạng thái không hợp lệ. Chỉ chấp nhận: {valid_statuses}")
        return self.repository.update_excursion_status(excursion_id, status)

    # ---------- Registration (business rule quan trọng nhất) ----------
    def register(self, passenger_id: int, activity_id: int = None, excursion_id: int = None):
        """Đăng ký hoạt động/tham quan bờ.
        Business Rule BR-02 (SRS): Không cho phép đăng ký vượt quá sức chứa.
        """
        if not activity_id and not excursion_id:
            raise ValueError("Phải chọn activity_id hoặc excursion_id")

        if activity_id:
            activity = self.repository.get_activity(activity_id)
            if not activity:
                raise ValueError("Không tìm thấy hoạt động")
            current_count = self.repository.count_registrations(activity_id=activity_id)
            if activity.capacity is not None and current_count >= activity.capacity:
                # Đúng message lỗi MSG01 trong SRS mục 3.6.3
                raise ValueError("Đăng ký thất bại. Hoạt động đã đạt sức chứa tối đa.")

        if excursion_id:
            excursion = self.repository.get_excursion(excursion_id)
            if not excursion:
                raise ValueError("Không tìm thấy chuyến tham quan bờ")
            current_count = self.repository.count_registrations(excursion_id=excursion_id)
            if excursion.capacity is not None and current_count >= excursion.capacity:
                raise ValueError("Đăng ký thất bại. Hoạt động đã đạt sức chứa tối đa.")

        return self.repository.add_registration({
            "passenger_id": passenger_id,
            "activity_id": activity_id,
            "excursion_id": excursion_id,
            "status": "registered",
        })

    def cancel_registration(self, registration_id: int):
        return self.repository.update_registration_status(registration_id, "cancelled")

    def list_registrations(self, activity_id: int = None, excursion_id: int = None, passenger_id: int = None):
        return self.repository.list_registrations(activity_id, excursion_id, passenger_id)
