from domain.models.checkin import CheckIn

class CheckInService:
    def __init__(self, repository):
        self.repository = repository

    def list_checkins(self):
        return self.repository.list()

    def create_checkin(self, passenger_id, booking_id=None, method='QR', code=None, checked_at=None):
        item = CheckIn(
            id=None,
            passenger_id=passenger_id,
            booking_id=booking_id,
            method=method,
            code=code,
            status='PENDING',
            checked_at=checked_at,
        )
        return self.repository.add(item)

    def update_status(self, checkin_id, status):
        allowed = {'PENDING', 'CHECKED_IN', 'FAILED'}
        if status not in allowed:
            return {'ok': False, 'message': 'Trạng thái không hợp lệ'}
        row = self.repository.update_status(checkin_id, status)
        if not row:
            return {'ok': False, 'message': 'Không tìm thấy check-in'}
        return {'ok': True, 'id': row.id, 'status': row.status}
