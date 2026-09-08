from flask import Blueprint, request, jsonify
from services.tour_provider_service import TourProviderService
from infrastructure.repositories.tour_provider_repository import TourProviderRepository
from api.schemas.tour_provider import TourProviderRequestSchema, TourProviderResponseSchema

bp = Blueprint('tour_provider', __name__, url_prefix='/tour-providers')
service = TourProviderService(TourProviderRepository())
req_schema = TourProviderRequestSchema()
res_schema = TourProviderResponseSchema()

@bp.route('/', methods=['GET'])
def list_providers():
    """
    List tour providers
    ---
    get:
      summary: Danh sách nhà cung cấp tour
      tags: [TourProviders]
      responses:
        200:
          description: OK
    """
    return jsonify(res_schema.dump(service.list_providers(), many=True)), 200

@bp.route('/', methods=['POST'])
def create_provider():
    """
    Create tour provider
    ---
    post:
      summary: Thêm nhà cung cấp tour
      tags: [TourProviders]
      responses:
        201:
          description: Created
    """
    data = request.get_json() or {}
    errors = req_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    row = service.create_provider(
        name=data['name'],
        contact_phone=data.get('contact_phone'),
        contact_email=data.get('contact_email'),
        address=data.get('address'),
    )
    return jsonify(res_schema.dump(row)), 201