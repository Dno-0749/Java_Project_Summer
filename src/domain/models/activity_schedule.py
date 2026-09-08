class ActivitySchedule:
    def __init__(self, id, activity_id, location, start_at, end_at, capacity, status):
        self.id = id
        self.activity_id = activity_id
        self.location = location
        self.start_at = start_at
        self.end_at = end_at
        self.capacity = capacity
        self.status = status 