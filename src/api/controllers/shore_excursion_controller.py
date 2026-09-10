from flask import Blueprint, request, jsonify
from services.shore_excursion_service import ShoreExcursionService
from infrastructure.repositories.shore_excursion_repository import ShoreExcursionRepository
from api.schemas.shore_excursion import (
    ShoreExcursionRequestSchema,
    ShoreExcursionResponseSchema,
    ShoreExcursionStatusSchema,
)

bp = Blueprint('shore_excursion', __name__, url_prefix='/shore-excursions')
service = ShoreExcursionService(ShoreExcursionRepository())
req_schema = ShoreExcursionRequestSchema()
res_schema = ShoreExcursionResponseSchema()
status_schema = ShoreExcursionStatusSchema()

@bp.route('/', methods=['GET'])
def list_excursions():
    """
    List shore excursions
    ---
    get:
      summary: Danh sách tour tham quan trên bờ
      tags: [ShoreExcursions]
      responses:
        200:
          description: OK
    """
    return jsonify(res_schema.dump(service.list_excursions(), many=True)), 200

@bp.route('/', methods=['POST'])
def create_excursion():
    """
    Create shore excursion
    ---
    post:
      summary: Tạo tour trên bờ
      tags: [ShoreExcursions]
      responses:
        201:
          description: Created
    """
    data = request.get_json() or {}
    errors = req_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    row = service.create_excursion(
        provider_id=data['provider_id'],
        name=data['name'],
        port_name=data.get('port_name'),
        description=data.get('description'),
        duration_hours=data.get('duration_hours'),
        capacity=data['capacity'],
        fee=data.get('fee', 0),
    )
    return jsonify(res_schema.dump(row)), 201

@bp.route('/<int:excursion_id>/status', methods=['PUT'])
def update_status(excursion_id):
    """
    Update excursion status
    ---
    put:
      summary: Cập nhật trạng thái tour (OPEN/CANCELLED/DELAYED/COMPLETED)
      tags: [ShoreExcursions]
      responses:
        200:
          description: OK
    """
    data = request.get_json() or {}
    errors = status_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = service.update_status(excursion_id, data['status'])
    return jsonify(result), (200 if result.get('ok') else 400)