class Activity:
    def __init__(
        self,
        id=None,
        name="",
        location="",
        description="",
        status="Sắp diễn ra",
        capacity=0,
        registered=0,
        price=0,
        activity_type="Miễn phí",
        rating=0,
        feedback_count=0,
        created_at=None,
        updated_at=None
    ):
        self.id = id
        self.name = name
        self.location = location
        self.description = description
        self.status = status
        self.capacity = capacity
        self.registered = registered
        self.price = price
        self.activity_type = activity_type
        self.rating = rating
        self.feedback_count = feedback_count
        self.created_at = created_at
        self.updated_at = updated_at