from flask import Blueprint, request, jsonify

from services.shore_excursion_service import ShoreExcursionService
from infrastructure.repositories.shore_excursion_repository import ShoreExcursionRepository


bp = Blueprint(
    "shore_excursion",
    __name__,
    url_prefix="/shore-excursions"
)


repository = ShoreExcursionRepository()
service = ShoreExcursionService(repository)


@bp.route("/", methods=["GET"])
def list_excursions():
    try:
        excursions = service.list_excursions()

        return jsonify([
            {
                "id": item.id,
                "provider_id": item.provider_id,
                "name": item.name,
                "date": item.date,
                "time": item.time,
                "location": item.location,
                "port_name": getattr(item, "port_name", None),
                "description": item.description,
                "duration_hours": getattr(item, "duration_hours", None),
                "capacity": item.capacity,
                "registered": item.registered,
                "fee": getattr(item, "fee", 0),
                "price": getattr(item, "price", getattr(item, "fee", 0)),
                "rating": getattr(item, "rating", 0),
                "feedback_count": getattr(item, "feedback_count", 0),
                "status": item.status
            }
            for item in excursions
        ]), 200

    except Exception as e:
        return jsonify({
            "ok": False,
            "message": str(e)
        }), 500


@bp.route("/", methods=["POST"])
def create_excursion():
    try:
        data = request.get_json() or {}

        if not data.get("provider_id"):
            return jsonify({
                "ok": False,
                "message": "provider_id là bắt buộc"
            }), 400

        if not data.get("name"):
            return jsonify({
                "ok": False,
                "message": "Tên tour là bắt buộc"
            }), 400

        item = service.create_excursion(
            provider_id=int(data["provider_id"]),
            name=data["name"],
            date=data.get("date"),
            time=data.get("time"),
            location=data.get("location"),
            port_name=data.get("port_name"),
            description=data.get("description"),
            duration_hours=data.get("duration_hours"),
            capacity=data.get("capacity", 0),
            fee=data.get("fee", data.get("price", 0)),
            price=data.get("price")
        )

        return jsonify({
            "ok": True,
            "message": "Tạo tour thành công",
            "data": {
                "id": item.id,
                "name": item.name
            }
        }), 201

    except Exception as e:
        return jsonify({
            "ok": False,
            "message": str(e)
        }), 500


@bp.route("/<int:excursion_id>", methods=["GET"])
def get_excursion(excursion_id):
    try:
        item = repository.get_by_id(excursion_id)

        if not item:
            return jsonify({
                "ok": False,
                "message": "Không tìm thấy tour"
            }), 404

        return jsonify({
            "id": item.id,
            "provider_id": item.provider_id,
            "name": item.name,
            "date": item.date,
            "time": item.time,
            "location": item.location,
            "port_name": getattr(item, "port_name", None),
            "description": item.description,
            "duration_hours": getattr(item, "duration_hours", None),
            "capacity": item.capacity,
            "registered": item.registered,
            "fee": getattr(item, "fee", 0),
            "price": getattr(item, "price", getattr(item, "fee", 0)),
            "rating": getattr(item, "rating", 0),
            "feedback_count": getattr(item, "feedback_count", 0),
            "status": item.status
        }), 200

    except Exception as e:
        return jsonify({
            "ok": False,
            "message": str(e)
        }), 500


@bp.route("/<int:excursion_id>", methods=["PUT"])
def update_excursion(excursion_id):
    try:
        data = request.get_json() or {}

        item = service.update_excursion(
            excursion_id,
            data
        )

        if not item:
            return jsonify({
                "ok": False,
                "message": "Không tìm thấy tour"
            }), 404

        return jsonify({
            "ok": True,
            "message": "Cập nhật tour thành công",
            "data": {
                "id": item.id,
                "name": item.name,
                "status": item.status
            }
        }), 200

    except Exception as e:
        return jsonify({
            "ok": False,
            "message": str(e)
        }), 500


@bp.route("/<int:excursion_id>/status", methods=["PUT"])
def update_status(excursion_id):
    try:
        data = request.get_json() or {}
        status = data.get("status")

        if not status:
            return jsonify({
                "ok": False,
                "message": "status là bắt buộc"
            }), 400

        result = service.update_status(
            excursion_id,
            status
        )

        if not result.get("ok"):
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "ok": False,
            "message": str(e)
        }), 500