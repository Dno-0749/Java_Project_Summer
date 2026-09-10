class ActivityRegistration:
    def __init__(self, id=None, passenger_id=None, activity_id=None, booking_id=None, status='REGISTERED', notes=None):
        self.id = id
        self.passenger_id = passenger_id
        self.activity_id = activity_id
        self.booking_id = booking_id
        self.status = status
        self.notes = notes
