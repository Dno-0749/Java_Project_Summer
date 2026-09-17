from flask import Blueprint, request, jsonify
from services.activity_schedule_service import ActivityScheduleService
from infrastructure.repositories.activity_schedule_repository import ActivityScheduleRepository
from api.schemas.activity_schedule import ActivityScheduleRequestSchema, ActivityScheduleResponseSchema

bp = Blueprint('activity_schedule', __name__, url_prefix='/activity-schedules')
service = ActivityScheduleService(ActivityScheduleRepository())
req_schema = ActivityScheduleRequestSchema()
res_schema = ActivityScheduleResponseSchema()


@bp.route('/', methods=['GET'])
def list_schedules():
    """
    List activity schedules
    ---
    get:
      summary: Danh sÃ¡ch lá»‹ch tá»• chá»©c hoáº¡t Ä‘á»™ng
      tags:
        - ActivitySchedules
      responses:
        200:
          description: OK
    """
    return jsonify(res_schema.dump(service.list_schedules(), many=True)), 200


@bp.route('/', methods=['POST'])
def create_schedule():
    """
    Create activity schedule
    ---
    post:
      summary: Thiáº¿t láº­p thá»i gian Ä‘á»‹a Ä‘iá»ƒm sá»©c chá»©a cho hoáº¡t Ä‘á»™ng
      tags:
        - ActivitySchedules
      responses:
        201:
          description: Created
    """
    data = request.get_json() or {}
    errors = req_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    row = service.create_schedule(
        activity_id=data['activity_id'],
        location=data.get('location'),
        start_at=data.get('start_at'),
        end_at=data.get('end_at'),
        capacity=data['capacity'],
    )
    return jsonify(res_schema.dump(row)), 201
