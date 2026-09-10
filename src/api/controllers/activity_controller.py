from datetime import datetime

from flask import Blueprint, jsonify, request

from infrastructure.models.activity_model import ActivityModel
from infrastructure.repositories.activity_repository import ActivityRepository

from api.schemas.activity import (
    ActivityRequestSchema,
    ActivityResponseSchema
)


bp = Blueprint(
    "activities_api",
    __name__,
    url_prefix="/api/activities"
)


repo = ActivityRepository()
request_schema = ActivityRequestSchema()
response_schema = ActivityResponseSchema()


@bp.get("/")
def list_activities():
    activities = repo.list()

    return jsonify(
        response_schema.dump(activities, many=True)
    ), 200


@bp.get("/<int:activity_id>")
def get_activity(activity_id):
    activity = repo.get(activity_id)

    if not activity:
        return jsonify({
            "message": "Activity not found"
        }), 404

    return jsonify(
        response_schema.dump(activity)
    ), 200


@bp.post("/")
def create_activity():
    data = request_schema.load(
        request.get_json() or {}
    )

    now = datetime.utcnow()

    activity = ActivityModel(
        **data,
        created_at=now,
        updated_at=now
    )

    activity = repo.add(activity)

    return jsonify(
        response_schema.dump(activity)
    ), 201


@bp.put("/<int:activity_id>")
def update_activity(activity_id):
    activity = repo.get(activity_id)

    if not activity:
        return jsonify({
            "message": "Activity not found"
        }), 404

    data = request_schema.load(
        request.get_json() or {}
    )

    data["updated_at"] = datetime.utcnow()

    activity = repo.update(
        activity,
        data
    )

    return jsonify(
        response_schema.dump(activity)
    ), 200


@bp.delete("/<int:activity_id>")
def delete_activity(activity_id):
    activity = repo.get(activity_id)

    if not activity:
        return jsonify({
            "message": "Activity not found"
        }), 404

    repo.delete(activity)

    return "", 204