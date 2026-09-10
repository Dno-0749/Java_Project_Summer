from domain.models.activity_registration import ActivityRegistration

class ActivityRegistrationService:
    def __init__(self, repository):
        self.repository = repository

    def list_registrations(self):
        return self.repository.list()

    def create_registration(self, passenger_id, activity_id, booking_id=None, notes=None):
        item = ActivityRegistration(
            id=None,
            passenger_id=passenger_id,
            activity_id=activity_id,
            booking_id=booking_id,
            status='REGISTERED',
            notes=notes,
        )
        return self.repository.add(item)

    def update_status(self, registration_id, status):
        allowed = {'REGISTERED', 'CONFIRMED', 'CANCELLED', 'COMPLETED'}
        if status not in allowed:
            return {'ok': False, 'message': 'Trạng thái không hợp lệ'}
        row = self.repository.update_status(registration_id, status)
        if not row:
            return {'ok': False, 'message': 'Không tìm thấy đăng ký hoạt động'}
        return {'ok': True, 'id': row.id, 'status': row.status}
