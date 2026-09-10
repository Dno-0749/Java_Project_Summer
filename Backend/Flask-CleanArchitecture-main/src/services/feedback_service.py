from infrastructure.repositories.feedback_repository import FeedbackRepository

VALID_TARGET_TYPES = ["activity", "excursion", "service", "cruise"]


class FeedbackService:
    def __init__(self, repository: FeedbackRepository = None):
        self.repository = repository or FeedbackRepository()

    def create(self, passenger_id: int, target_type: str, rating: int,
               target_id: int = None, target_name: str = None, comment: str = None):
        if target_type not in VALID_TARGET_TYPES:
            raise ValueError(f"target_type không hợp lệ. Chỉ chấp nhận: {VALID_TARGET_TYPES}")
        if rating is None or not (1 <= int(rating) <= 5):
            raise ValueError("Đánh giá (rating) phải từ 1 đến 5 sao")

        return self.repository.create({
            "passenger_id": passenger_id,
            "target_type": target_type,
            "target_id": target_id,
            "target_name": target_name,
            "rating": int(rating),
            "comment": comment,
        })

    def list_by_passenger(self, passenger_id: int):
        return self.repository.list_by_passenger(passenger_id)

    def list_by_target(self, target_type: str, target_id: int = None):
        return self.repository.list_by_target(target_type, target_id)
