from flask import Blueprint, jsonify, request

from services.activity_registration_service import ActivityRegistrationService


bp = Blueprint(
    "activity_registration",
    __name__,
    url_prefix="/api/activity-registrations"
)

service = ActivityRegistrationService()


def registration_to_dict(registration):
    return {
        "id": registration.id,
        "passenger_id": registration.passenger_id,
        "activity_id": registration.activity_id,
        "booking_id": registration.booking_id,
        "status": registration.status,
        "notes": registration.notes
    }


@bp.get("/")
def list_registrations():
    registrations = service.list()

    return jsonify([
        registration_to_dict(item)
        for item in registrations
    ]), 200


@bp.get("/<int:registration_id>")
def get_registration(registration_id):
    registration = service.get(registration_id)

    if not registration:
        return jsonify({
            "message": "Registration not found"
        }), 404

    return jsonify(
        registration_to_dict(registration)
    ), 200


@bp.get("/activity/<int:activity_id>")
def get_activity_registrations(activity_id):
    registrations = service.get_by_activity(activity_id)

    return jsonify([
        registration_to_dict(item)
        for item in registrations
    ]), 200


@bp.get("/passenger/<int:passenger_id>")
def get_passenger_registrations(passenger_id):
    registrations = service.get_by_passenger(passenger_id)

    return jsonify([
        registration_to_dict(item)
        for item in registrations
    ]), 200


@bp.post("/")
def create_registration():
    data = request.get_json() or {}

    required = ["passenger_id", "activity_id"]

    for field in required:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    registration = service.create(data)

    return jsonify(
        registration_to_dict(registration)
    ), 201


@bp.put("/<int:registration_id>")
def update_registration(registration_id):
    data = request.get_json() or {}

    registration = service.update(
        registration_id,
        data
    )

    if not registration:
        return jsonify({
            "message": "Registration not found"
        }), 404

    return jsonify(
        registration_to_dict(registration)
    ), 200


@bp.delete("/<int:registration_id>")
def delete_registration(registration_id):
    deleted = service.delete(registration_id)

    if not deleted:
        return jsonify({
            "message": "Registration not found"
        }), 404

    return "", 204