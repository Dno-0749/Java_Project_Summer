from infrastructure.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, repository: NotificationRepository = None):
        self.repository = repository or NotificationRepository()

    def create(self, title: str, content: str = None, passenger_id: int = None,
               cruise_id: int = None, category: str = "general", priority: str = "normal"):
        if not title:
            raise ValueError("Thiếu title")
        return self.repository.create({
            "passenger_id": passenger_id,
            "cruise_id": cruise_id,
            "title": title,
            "content": content,
            "category": category,
            "priority": priority,
        })

    def list_for_passenger(self, passenger_id: int, cruise_id: int = None):
        return self.repository.list_for_passenger(passenger_id, cruise_id)

    def mark_read(self, notification_id: int):
        return self.repository.mark_read(notification_id)
