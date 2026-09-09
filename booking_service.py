from domain.models.booking import Booking

class BookingService:
    def __init__(self, repository):
        self.repository = repository

    def list_bookings(self):
        return self.repository.list()

    def create_booking(self, passenger_id, cabin_id=None, booking_code=None, start_date=None, end_date=None):
        item = Booking(
            id=None,
            passenger_id=passenger_id,
            cabin_id=cabin_id,
            booking_code=booking_code,
            start_date=start_date,
            end_date=end_date,
            status='PENDING',
        )
        return self.repository.add(item)

    def update_status(self, booking_id, status):
        allowed = {'PENDING', 'CONFIRMED', 'CANCELLED', 'CHECKED_IN'}
        if status not in allowed:
            return {'ok': False, 'message': 'Trạng thái không hợp lệ'}
        row = self.repository.update_status(booking_id, status)
        if not row:
            return {'ok': False, 'message': 'Không tìm thấy booking'}
        return {'ok': True, 'id': row.id, 'status': row.status}
