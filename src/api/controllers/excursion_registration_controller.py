from flask import Blueprint, request, jsonify
from services.excursion_registration_service import ExcursionRegistrationService
from infrastructure.repositories.excursion_registration_repository import ExcursionRegistrationRepository

bp = Blueprint('excursion_registration', __name__, url_prefix='/excursion-registrations')
service = ExcursionRegistrationService(ExcursionRegistrationRepository())

@bp.route('/', methods=['GET'])
def list_excursion_registrations():
    rows = service.list_registrations()
    return jsonify([
        {
            'id': row.id,
            'passenger_id': row.passenger_id,
            'excursion_id': row.excursion_id,
            'booking_id': row.booking_id,
            'status': row.status,
            'notes': row.notes,
        } for row in rows
    ]), 200

@bp.route('/', methods=['POST'])
def create_excursion_registration():
    data = request.get_json() or {}
    passenger_id = data.get('passenger_id')
    excursion_id = data.get('excursion_id')
    if not passenger_id or not excursion_id:
        return jsonify({'message': 'passenger_id và excursion_id là bắt buộc'}), 400
    row = service.create_registration(
        passenger_id=passenger_id,
        excursion_id=excursion_id,
        booking_id=data.get('booking_id'),
        notes=data.get('notes'),
    )
    return jsonify({
        'id': row.id,
        'passenger_id': row.passenger_id,
        'excursion_id': row.excursion_id,
        'booking_id': row.booking_id,
        'status': row.status,
        'notes': row.notes,
    }), 201

@bp.route('/<int:registration_id>/status', methods=['PUT'])
def update_excursion_registration_status(registration_id):
    data = request.get_json() or {}
    status = data.get('status')
    if not status:
        return jsonify({'message': 'status là bắt buộc'}), 400
    return jsonify(service.update_status(registration_id, status)), 200
