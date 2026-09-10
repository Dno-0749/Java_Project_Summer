class ActivitySchedule:
    def __init__(
        self,
        id=None,
        activity_id=None,
        date=None,
        start_time=None,
        end_time=None,
        location='',
        capacity=0,
        created_at=None,
        updated_at=None
    ):
        self.id = id
        self.activity_id = activity_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.capacity = capacity
        self.created_at = created_at
        self.updated_at = updated_at