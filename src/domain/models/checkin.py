class CheckIn:
    def __init__(self, id=None, passenger_id=None, booking_id=None, method='QR', code=None, status='PENDING', checked_at=None):
        self.id = id
        self.passenger_id = passenger_id
        self.booking_id = booking_id
        self.method = method
        self.code = code
        self.status = status
        self.checked_at = checked_at
