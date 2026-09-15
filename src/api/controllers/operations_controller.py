from flask import Blueprint, jsonify, request

from services.operations_service import OperationsService


bp = Blueprint("operations", __name__, url_prefix="/operations")
service = OperationsService()


def _required(data, *fields):
    missing = [field for field in fields if data.get(field) in (None, "")]
    if missing:
        return jsonify({"message": "Missing required fields", "fields": missing}), 400
    return None


@bp.get("/dashboard")
def dashboard():
    """Return live operational metrics."""
    return jsonify(service.dashboard()), 200


@bp.route("/activities", methods=["GET", "POST"])
def activities():
    if request.method == "GET":
        return jsonify(service.list_activities()), 200
    data = request.get_json(silent=True) or {}
    error = _required(data, "name", "capacity")
    if error:
        return error
    try:
        return jsonify(service.create_activity(data)), 201
    except (TypeError, ValueError) as exc:
        return jsonify({"message": str(exc)}), 400


@bp.post("/activities/<int:activity_id>/participants")
def add_participant(activity_id):
    data = request.get_json(silent=True) or {}
    error = _required(data, "passenger_id")
    if error:
        return error
    try:
        return jsonify(service.add_participant(activity_id, data)), 201
    except KeyError as exc:
        return jsonify({"message": str(exc).strip("'")}), 404
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 409


@bp.route("/checkins", methods=["GET", "POST"])
def checkins():
    if request.method == "GET":
        return jsonify(service.list_checkins(request.args.get("status"))), 200
    data = request.get_json(silent=True) or {}
    error = _required(data, "passenger_id")
    if error:
        return error
    return jsonify(service.record_checkin(data)), 201


@bp.get("/late-return-risks")
def late_return_risks():
    return jsonify(service.late_return_risks()), 200


@bp.post("/transactions")
def transactions():
    data = request.get_json(silent=True) or {}
    error = _required(data, "amount")
    if error:
        return error
    try:
        return jsonify(service.record_transaction(data)), 201
    except (TypeError, ValueError) as exc:
        return jsonify({"message": str(exc)}), 400


@bp.route("/reports/<trip_id>", methods=["GET", "PUT"])
def trip_report(trip_id):
    if request.method == "GET":
        report = service.get_report(trip_id)
        if not report:
            return jsonify({"message": "Report not found"}), 404
        return jsonify(report), 200
    return jsonify(service.save_report(trip_id, request.get_json(silent=True) or {})), 200