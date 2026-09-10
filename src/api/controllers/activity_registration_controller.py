from flask import Blueprint, request, jsonify
from services.activity_registration_service import ActivityRegistrationService
from infrastructure.repositories.activity_registration_repository import ActivityRegistrationRepository

bp = Blueprint('activity_registration', __name__, url_prefix='/activity-registrations')
service = ActivityRegistrationService(ActivityRegistrationRepository())

@bp.route('/', methods=['GET'])
def list_activity_registrations():
    rows = service.list_registrations()
    return jsonify([
        {
            'id': row.id,
            'passenger_id': row.passenger_id,
            'activity_id': row.activity_id,
            'booking_id': row.booking_id,
            'status': row.status,
            'notes': row.notes,
        } for row in rows
    ]), 200

@bp.route('/', methods=['POST'])
def create_activity_registration():
    data = request.get_json() or {}
    passenger_id = data.get('passenger_id')
    activity_id = data.get('activity_id')
    if not passenger_id or not activity_id:
        return jsonify({'message': 'passenger_id và activity_id là bắt buộc'}), 400
    row = service.create_registration(
        passenger_id=passenger_id,
        activity_id=activity_id,
        booking_id=data.get('booking_id'),
        notes=data.get('notes'),
    )
    return jsonify({
        'id': row.id,
        'passenger_id': row.passenger_id,
        'activity_id': row.activity_id,
        'booking_id': row.booking_id,
        'status': row.status,
        'notes': row.notes,
    }), 201

@bp.route('/<int:registration_id>/status', methods=['PUT'])
def update_activity_registration_status(registration_id):
    data = request.get_json() or {}
    status = data.get('status')
    if not status:
        return jsonify({'message': 'status là bắt buộc'}), 400
    return jsonify(service.update_status(registration_id, status)), 200
