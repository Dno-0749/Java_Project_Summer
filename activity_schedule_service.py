from domain.models.activity_schedule import ActivitySchedule

class ActivityScheduleService:
    def __init__(self, repository):
        self.repository = repository

    def list_schedules(self):
        return self.repository.list()

    def create_schedule(self, activity_id, location, start_at, end_at, capacity):
        item = ActivitySchedule(
            id=None,
            activity_id=activity_id,
            location=location,
            start_at=start_at,
            end_at=end_at,
            capacity=int(capacity or 0),
            status='SCHEDULED',
        )
        return self.repository.add(item)