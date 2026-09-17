class ShoreExcursion:
    def __init__(
        self,
        id=None,
        name='',
        date=None,
        time='',
        location='',
        provider_id=None,
        capacity=0,
        registered=0,
        price=0,
        status='Sắp diễn ra',
        description='',
        created_at=None,
        updated_at=None
    ):
        self.id = id
        self.name = name
        self.date = date
        self.time = time
        self.location = location
        self.provider_id = provider_id
        self.capacity = capacity
        self.registered = registered
        self.price = price
        self.status = status
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
