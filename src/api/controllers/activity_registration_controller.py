from flask import Blueprint, jsonify, request

from services.activity_registration_service import (
    ActivityRegistrationService
)


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
        "notes": registration.notes,
        "rating": registration.rating,
        "feedback": registration.feedback
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

    registration = service.get(
        registration_id
    )

    if not registration:
        return jsonify({
            "message": "Registration not found"
        }), 404

    return jsonify(
        registration_to_dict(registration)
    ), 200


@bp.get("/activity/<int:activity_id>")
def get_activity_registrations(activity_id):

    registrations = service.get_by_activity(
        activity_id
    )

    return jsonify([
        registration_to_dict(item)
        for item in registrations
    ]), 200


@bp.post("/")
def create_registration():

    data = request.get_json() or {}

    if "passenger_id" not in data:
        return jsonify({
            "message": "passenger_id is required"
        }), 400

    if "activity_id" not in data:
        return jsonify({
            "message": "activity_id is required"
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


# =========================
# CHECK-IN
# =========================

@bp.post("/<int:registration_id>/checkin")
def checkin_registration(registration_id):

    registration = service.get(
        registration_id
    )

    if not registration:
        return jsonify({
            "message": "Registration not found"
        }), 404

    registration = service.update(
        registration_id,
        {
            "status": "CHECKED_IN"
        }
    )

    return jsonify({
        "message": "Check-in successful",
        "registration": registration_to_dict(
            registration
        )
    }), 200


# =========================
# CANCEL
# =========================

@bp.post("/<int:registration_id>/cancel")
def cancel_registration(registration_id):

    registration = service.get(
        registration_id
    )

    if not registration:
        return jsonify({
            "message": "Registration not found"
        }), 404

    registration = service.update(
        registration_id,
        {
            "status": "CANCELLED"
        }
    )

    return jsonify({
        "message": "Registration cancelled",
        "registration": registration_to_dict(
            registration
        )
    }), 200


# =========================
# PARTICIPATION RATE
# =========================

@bp.get(
    "/activity/<int:activity_id>/participation-rate"
)
def participation_rate(activity_id):

    registrations = service.get_by_activity(
        activity_id
    )

    total_registered = len([
        item
        for item in registrations
        if item.status != "CANCELLED"
    ])

    checked_in = len([
        item
        for item in registrations
        if item.status == "CHECKED_IN"
    ])

    rate = 0

    if total_registered > 0:
        rate = round(
            checked_in / total_registered * 100,
            2
        )

    return jsonify({
        "activity_id": activity_id,
        "total_registered": total_registered,
        "checked_in": checked_in,
        "participation_rate": rate
    }), 200


# =========================
# FEEDBACK
# =========================

@bp.post("/<int:registration_id>/feedback")
def submit_feedback(registration_id):

    registration = service.get(
        registration_id
    )

    if not registration:
        return jsonify({
            "message": "Registration not found"
        }), 404

    data = request.get_json() or {}

    rating = data.get("rating")
    feedback = data.get("feedback", "")

    if rating is None:
        return jsonify({
            "message": "rating is required"
        }), 400

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({
            "message": "rating must be between 1 and 5"
        }), 400

    registration = service.update(
        registration_id,
        {
            "rating": rating,
            "feedback": feedback
        }
    )

    return jsonify({
        "message": "Feedback submitted successfully",
        "registration": registration_to_dict(
            registration
        )
    }), 200


# =========================
# DELETE
# =========================

@bp.delete("/<int:registration_id>")
def delete_registration(registration_id):

    deleted = service.delete(
        registration_id
    )

    if not deleted:
        return jsonify({
            "message": "Registration not found"
        }), 404

    return "", 204