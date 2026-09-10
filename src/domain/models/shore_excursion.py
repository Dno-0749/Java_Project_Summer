class ShoreExcursion:
    def __init__(
        self,
        id,
        provider_id,
        name,
        port_name,
        description,
        duration_hours,
        capacity,
        fee,
        status,
    ):
        self.id = id
        self.provider_id = provider_id
        self.name = name
        self.port_name = port_name
        self.description = description
        self.duration_hours = duration_hours
        self.capacity = capacity
        self.fee = fee
        self.status = status  
        