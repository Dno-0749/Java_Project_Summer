from flask import Blueprint, request, jsonify

from services.excursion_registration_service import (
    ExcursionRegistrationService
)


excursion_registration_bp = Blueprint(
    "excursion_registration",
    __name__,
    url_prefix="/excursion-registrations"
)

service = ExcursionRegistrationService()


def serialize_registration(item):
    return {
        "id": item.id,
        "passenger_id": item.passenger_id,
        "excursion_id": item.excursion_id,
        "booking_id": item.booking_id,
        "guest_code": item.guest_code,
        "passenger_name": item.passenger_name,
        "room": item.room,
        "status": item.status,
        "notes": item.notes,
        "checked_in": item.checked_in,
        "checked_in_at": (
            item.checked_in_at.isoformat()
            if item.checked_in_at
            else None
        ),
        "registered_at": (
            item.registered_at.isoformat()
            if item.registered_at
            else None
        )
    }


@excursion_registration_bp.route("/", methods=["GET"])
def list_registrations():
    excursion_id = request.args.get(
        "excursion_id",
        type=int
    )

    registrations = service.list_registrations(
        excursion_id
    )

    return jsonify([
        serialize_registration(item)
        for item in registrations
    ])


@excursion_registration_bp.route("/", methods=["POST"])
def create_registration():
    data = request.get_json() or {}

    if not data.get("excursion_id"):
        return jsonify({
            "message": "Thiếu excursion_id."
        }), 400

    try:
        registration = service.create_registration(
            passenger_id=data.get("passenger_id"),
            excursion_id=data.get("excursion_id"),
            booking_id=data.get("booking_id"),
            guest_code=data.get("guest_code"),
            passenger_name=data.get("passenger_name"),
            room=data.get("room"),
            status=data.get(
                "status",
                "REGISTERED"
            ),
            notes=data.get("notes")
        )

        return jsonify(
            serialize_registration(registration)
        ), 201

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "message": str(e)
        }), 500


@excursion_registration_bp.route(
    "/<int:registration_id>/status",
    methods=["PUT"]
)
def update_registration_status(
    registration_id
):
    data = request.get_json() or {}

    status = data.get("status")

    if not status:
        return jsonify({
            "message": "Thiếu status."
        }), 400

    try:
        registration = service.update_status(
            registration_id,
            status
        )

        if registration is None:
            return jsonify({
                "message": "Không tìm thấy đăng ký."
            }), 404

        return jsonify(
            serialize_registration(registration)
        )

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "message": str(e)
        }), 500


@excursion_registration_bp.route(
    "/<int:registration_id>/checkin",
    methods=["PUT"]
)
def checkin_registration(
    registration_id
):
    try:
        registration = service.check_in(
            registration_id
        )

        if registration is None:
            return jsonify({
                "message": "Không tìm thấy đăng ký."
            }), 404

        return jsonify(
            serialize_registration(registration)
        )

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "message": str(e)
        }), 500
