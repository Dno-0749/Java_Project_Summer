from flask import Blueprint, request, jsonify
from services.checkin_service import CheckInService
from infrastructure.repositories.checkin_repository import CheckInRepository

bp = Blueprint('checkin', __name__, url_prefix='/checkins')
service = CheckInService(CheckInRepository())

@bp.route('/', methods=['GET'])
def list_checkins():
    rows = service.list_checkins()
    return jsonify([
        {
            'id': row.id,
            'passenger_id': row.passenger_id,
            'booking_id': row.booking_id,
            'method': row.method,
            'code': row.code,
            'status': row.status,
            'checked_at': row.checked_at,
        } for row in rows
    ]), 200

@bp.route('/', methods=['POST'])
def create_checkin():
    data = request.get_json() or {}
    passenger_id = data.get('passenger_id')
    if not passenger_id:
        return jsonify({'message': 'passenger_id là bắt buộc'}), 400
    row = service.create_checkin(
        passenger_id=passenger_id,
        booking_id=data.get('booking_id'),
        method=data.get('method', 'QR'),
        code=data.get('code'),
        checked_at=data.get('checked_at'),
    )
    return jsonify({
        'id': row.id,
        'passenger_id': row.passenger_id,
        'booking_id': row.booking_id,
        'method': row.method,
        'code': row.code,
        'status': row.status,
        'checked_at': row.checked_at,
    }), 201

@bp.route('/<int:checkin_id>/status', methods=['PUT'])
def update_checkin_status(checkin_id):
    data = request.get_json() or {}
    status = data.get('status')
    if not status:
        return jsonify({'message': 'status là bắt buộc'}), 400
    return jsonify(service.update_status(checkin_id, status)), 200
