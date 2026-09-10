from flask import Blueprint, request, jsonify
from services.itinerary_service import ItineraryService
from api.schemas.itinerary import (
    CruiseRequestSchema, CruiseResponseSchema,
    PortRequestSchema, PortResponseSchema,
    CruiseDayRequestSchema, CruiseDayResponseSchema,
    CabinRequestSchema, CabinResponseSchema,
)

bp = Blueprint("itinerary", __name__)
service = ItineraryService()

cruise_req = CruiseRequestSchema()
cruise_res = CruiseResponseSchema()
port_req = PortRequestSchema()
port_res = PortResponseSchema()
day_req = CruiseDayRequestSchema()
day_res = CruiseDayResponseSchema()
cabin_req = CabinRequestSchema()
cabin_res = CabinResponseSchema()


# ==================== CRUISE ====================
@bp.route("/cruises", methods=["GET"])
def list_cruises():
    """
    Lấy danh sách chuyến cruise
    ---
    get:
      summary: Lấy danh sách toàn bộ chuyến cruise
      tags:
        - Itinerary
      responses:
        200:
          description: Danh sách cruise
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CruiseResponse'
    """
    cruises = service.list_cruises()
    return jsonify(cruise_res.dump(cruises, many=True)), 200


@bp.route("/cruises/<int:cruise_id>", methods=["GET"])
def get_cruise(cruise_id):
    """
    Lấy chi tiết 1 chuyến cruise
    ---
    get:
      summary: Lấy chi tiết 1 chuyến cruise theo id
      tags:
        - Itinerary
      parameters:
        - name: cruise_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Thông tin cruise
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CruiseResponse'
        404:
          description: Không tìm thấy cruise
    """
    cruise = service.get_cruise(cruise_id)
    if not cruise:
        return jsonify({"message": "Cruise not found"}), 404
    return jsonify(cruise_res.dump(cruise)), 200


@bp.route("/cruises", methods=["POST"])
def create_cruise():
    """
    Tạo chuyến cruise mới
    ---
    post:
      summary: Tạo chuyến cruise mới (UC12 - Tạo chuyến du lịch nhiều ngày)
      tags:
        - Itinerary
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CruiseRequest'
      responses:
        201:
          description: Tạo thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CruiseResponse'
        400:
          description: Dữ liệu không hợp lệ (ví dụ ngày kết thúc trước ngày bắt đầu)
    """
    data = request.get_json()
    errors = cruise_req.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        cruise = service.create_cruise(cruise_req.load(data))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(cruise_res.dump(cruise)), 201


@bp.route("/cruises/<int:cruise_id>", methods=["PUT"])
def update_cruise(cruise_id):
    """
    Cập nhật chuyến cruise
    ---
    put:
      summary: Cập nhật thông tin chuyến cruise
      tags:
        - Itinerary
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
              $ref: '#/components/schemas/CruiseRequest'
      responses:
        200:
          description: Cập nhật thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CruiseResponse'
        400:
          description: Dữ liệu không hợp lệ
        404:
          description: Không tìm thấy cruise
    """
    data = request.get_json()
    try:
        cruise = service.update_cruise(cruise_id, data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not cruise:
        return jsonify({"message": "Cruise not found"}), 404
    return jsonify(cruise_res.dump(cruise)), 200


@bp.route("/cruises/<int:cruise_id>", methods=["DELETE"])
def delete_cruise(cruise_id):
    """
    Xóa chuyến cruise
    ---
    delete:
      summary: Xóa 1 chuyến cruise
      tags:
        - Itinerary
      parameters:
        - name: cruise_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        204:
          description: Xóa thành công
        404:
          description: Không tìm thấy cruise
    """
    ok = service.delete_cruise(cruise_id)
    if not ok:
        return jsonify({"message": "Cruise not found"}), 404
    return "", 204


# ==================== PORT ====================
@bp.route("/ports", methods=["GET"])
def list_ports():
    """
    Lấy danh sách cảng
    ---
    get:
      summary: Lấy danh sách cảng (dùng khi tạo cruise day)
      tags:
        - Itinerary
      responses:
        200:
          description: Danh sách cảng
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/PortResponse'
    """
    ports = service.list_ports()
    return jsonify(port_res.dump(ports, many=True)), 200


@bp.route("/ports", methods=["POST"])
def create_port():
    """
    Tạo cảng mới
    ---
    post:
      summary: Tạo mới 1 cảng (UC34 - Quản lý tàu/khu vực/điểm dừng)
      tags:
        - Itinerary
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PortRequest'
      responses:
        201:
          description: Tạo thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PortResponse'
        400:
          description: Dữ liệu không hợp lệ
    """
    data = request.get_json()
    errors = port_req.validate(data)
    if errors:
        return jsonify(errors), 400
    port = service.create_port(port_req.load(data))
    return jsonify(port_res.dump(port)), 201


# ==================== CRUISE DAY ====================
@bp.route("/cruises/<int:cruise_id>/days", methods=["GET"])
def list_cruise_days(cruise_id):
    """
    Lấy lịch trình theo ngày
    ---
    get:
      summary: Lấy lịch trình theo ngày của 1 chuyến cruise (UC05)
      tags:
        - Itinerary
      parameters:
        - name: cruise_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Danh sách ngày lịch trình
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CruiseDayResponse'
    """
    days = service.list_cruise_days(cruise_id)
    return jsonify(day_res.dump(days, many=True)), 200


@bp.route("/cruises/<int:cruise_id>/days", methods=["POST"])
def create_cruise_day(cruise_id):
    """
    Thêm ngày lịch trình
    ---
    post:
      summary: Thêm 1 ngày lịch trình + cảng ghé thăm (UC13 - Quản lý cảng ghé thăm)
      tags:
        - Itinerary
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
              $ref: '#/components/schemas/CruiseDayRequest'
      responses:
        201:
          description: Tạo thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CruiseDayResponse'
        400:
          description: Dữ liệu không hợp lệ (ví dụ giờ rời bến trước giờ cập bến)
    """
    data = request.get_json()
    data["cruise_id"] = cruise_id
    errors = day_req.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        day = service.create_cruise_day(day_req.load(data))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(day_res.dump(day)), 201


@bp.route("/cruise-days/<int:day_id>", methods=["PUT"])
def update_cruise_day(day_id):
    """
    Cập nhật ngày lịch trình
    ---
    put:
      summary: Cập nhật ngày lịch trình (UC14 - Cập nhật thay đổi lịch trình)
      tags:
        - Itinerary
      parameters:
        - name: day_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CruiseDayRequest'
      responses:
        200:
          description: Cập nhật thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CruiseDayResponse'
        400:
          description: Dữ liệu không hợp lệ
        404:
          description: Không tìm thấy cruise day
    """
    data = request.get_json()
    errors = day_req.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400
    loaded = day_req.load(data, partial=True)
    try:
        day = service.update_cruise_day(day_id, loaded)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not day:
        return jsonify({"message": "Cruise day not found"}), 404
    return jsonify(day_res.dump(day)), 200


# ==================== CABIN ====================
@bp.route("/cruises/<int:cruise_id>/cabins", methods=["GET"])
def list_cabins(cruise_id):
    """
    Lấy danh sách cabin
    ---
    get:
      summary: Lấy danh sách cabin của 1 chuyến cruise
      tags:
        - Itinerary
      parameters:
        - name: cruise_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Danh sách cabin
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CabinResponse'
    """
    cabins = service.list_cabins(cruise_id)
    return jsonify(cabin_res.dump(cabins, many=True)), 200


@bp.route("/cruises/<int:cruise_id>/cabins", methods=["POST"])
def create_cabin(cruise_id):
    """
    Tạo cabin mới
    ---
    post:
      summary: Tạo cabin mới cho 1 chuyến cruise
      tags:
        - Itinerary
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
              $ref: '#/components/schemas/CabinRequest'
      responses:
        201:
          description: Tạo thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CabinResponse'
        400:
          description: Dữ liệu không hợp lệ
    """
    data = request.get_json()
    data["cruise_id"] = cruise_id
    errors = cabin_req.validate(data)
    if errors:
        return jsonify(errors), 400
    cabin = service.create_cabin(cabin_req.load(data))
    return jsonify(cabin_res.dump(cabin)), 201
