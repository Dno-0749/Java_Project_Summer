from flask import Blueprint, request, jsonify
from services.passenger_service import PassengerService
from api.schemas.passenger import PassengerRequestSchema, PassengerResponseSchema

bp = Blueprint("passenger", __name__)
service = PassengerService()

passenger_req = PassengerRequestSchema()
passenger_res = PassengerResponseSchema()


@bp.route("/cruises/<int:cruise_id>/passengers", methods=["GET"])
def list_passengers(cruise_id):
    """
    Danh sách hành khách
    ---
    get:
      summary: Lấy danh sách hành khách của 1 chuyến cruise
      tags:
        - Passenger
      parameters:
        - name: cruise_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Danh sách hành khách
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/PassengerResponse'
    """
    passengers = service.list_by_cruise(cruise_id)
    return jsonify(passenger_res.dump(passengers, many=True)), 200


@bp.route("/passengers/<int:passenger_id>", methods=["GET"])
def get_passenger(passenger_id):
    """
    Chi tiết hành khách
    ---
    get:
      summary: Lấy thông tin 1 hành khách
      tags:
        - Passenger
      parameters:
        - name: passenger_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Thông tin hành khách
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PassengerResponse'
        404:
          description: Không tìm thấy
    """
    passenger = service.get(passenger_id)
    if not passenger:
        return jsonify({"message": "Passenger not found"}), 404
    return jsonify(passenger_res.dump(passenger)), 200


@bp.route("/passengers/lookup/<string:code>", methods=["GET"])
def lookup_passenger(code):
    """
    Tra cứu theo mã QR/RFID
    ---
    get:
      summary: Tìm hành khách theo qr_code hoặc rfid_code - dùng cho bước xác thực tại POS (UC22)
      tags:
        - Passenger
      parameters:
        - name: code
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Thông tin hành khách
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PassengerResponse'
        404:
          description: Mã không hợp lệ
    """
    passenger = service.get_by_code(code)
    if not passenger:
        return jsonify({"message": "Mã định danh không hợp lệ"}), 404
    return jsonify(passenger_res.dump(passenger)), 200


@bp.route("/cruises/<int:cruise_id>/passengers", methods=["POST"])
def create_passenger(cruise_id):
    """
    Tạo hành khách mới
    ---
    post:
      summary: Tạo hành khách mới cho 1 chuyến cruise (tự sinh qr_code)
      tags:
        - Passenger
      parameters:
        - name: cruise_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [full_name]
              properties:
                full_name:
                  type: string
                cabin_id:
                  type: integer
      responses:
        201:
          description: Tạo thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PassengerResponse'
        400:
          description: Dữ liệu không hợp lệ
    """
    data = request.get_json()
    if not data or not data.get("full_name"):
        return jsonify({"error": "Thiếu full_name"}), 400
    passenger = service.create(cruise_id, data["full_name"], data.get("cabin_id"))
    return jsonify(passenger_res.dump(passenger)), 201
