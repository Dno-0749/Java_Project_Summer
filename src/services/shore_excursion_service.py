from domain.models.shore_excursion import ShoreExcursion

class ShoreExcursionService:
    def __init__(self, repository):
        self.repository = repository

    def list_excursions(self):
        return self.repository.list()

    def create_excursion(self, provider_id, name, port_name, description, duration_hours, capacity, fee):
        item = ShoreExcursion(
            id=None,
            provider_id=provider_id,
            name=name,
            port_name=port_name,
            description=description,
            duration_hours=duration_hours,
            capacity=int(capacity or 0),
            fee=float(fee or 0),
            status='OPEN',
        )
        return self.repository.add(item)

    def update_status(self, excursion_id, status):
        allowed = {'OPEN', 'CANCELLED', 'DELAYED', 'COMPLETED'}
        if status not in allowed:
            return {'ok': False, 'message': 'Trạng thái không hợp lệ'}
        row = self.repository.update_status(excursion_id, status)
        if not row:
            return {'ok': False, 'message': 'Không tìm thấy tour'}
        return {'ok': True, 'id': row.id, 'status': row.status}