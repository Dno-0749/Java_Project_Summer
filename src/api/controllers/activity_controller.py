from flask import Blueprint, request, jsonify
from services.activity_service import ActivityService
from api.schemas.activity import (
    ActivityRequestSchema, ActivityResponseSchema,
    ExcursionRequestSchema, ExcursionResponseSchema,
    RegistrationRequestSchema, RegistrationResponseSchema,
)

bp = Blueprint("activity", __name__)
service = ActivityService()

activity_req = ActivityRequestSchema()
activity_res = ActivityResponseSchema()
excursion_req = ExcursionRequestSchema()
excursion_res = ExcursionResponseSchema()
registration_req = RegistrationRequestSchema()
registration_res = RegistrationResponseSchema()


# ==================== ACTIVITY ====================
@bp.route("/cruises/<int:cruise_id>/activities", methods=["GET"])
def list_activities(cruise_id):
    """
    Danh sách hoạt động
    ---
    get:
      summary: Xem hoạt động trên tàu (UC06)
      tags:
        - Activity
      parameters:
        - name: cruise_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Danh sách hoạt động
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/ActivityResponse'
    """
    activities = service.list_activities(cruise_id)
    return jsonify(activity_res.dump(activities, many=True)), 200


@bp.route("/activities/<int:activity_id>", methods=["GET"])
def get_activity(activity_id):
    """
    Chi tiết hoạt động
    ---
    get:
      summary: Lấy chi tiết 1 hoạt động
      tags:
        - Activity
      parameters:
        - name: activity_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Thông tin hoạt động
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ActivityResponse'
        404:
          description: Không tìm thấy
    """
    activity = service.get_activity(activity_id)
    if not activity:
        return jsonify({"message": "Activity not found"}), 404
    return jsonify(activity_res.dump(activity)), 200


@bp.route("/cruises/<int:cruise_id>/activities", methods=["POST"])
def create_activity(cruise_id):
    """
    Tạo hoạt động mới
    ---
    post:
      summary: Tạo hoạt động trên tàu (UC15)
      tags:
        - Activity
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
              $ref: '#/components/schemas/ActivityRequest'
      responses:
        201:
          description: Tạo thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ActivityResponse'
        400:
          description: Dữ liệu không hợp lệ (sức chứa phải > 0)
    """
    data = request.get_json()
    data["cruise_id"] = cruise_id
    errors = activity_req.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        activity = service.create_activity(activity_req.load(data))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(activity_res.dump(activity)), 201


# ==================== SHORE EXCURSION ====================
@bp.route("/cruise-days/<int:cruise_day_id>/excursions", methods=["GET"])
def list_excursions(cruise_day_id):
    """
    Danh sách tour trên bờ
    ---
    get:
      summary: Xem danh sách tour trên bờ theo ngày lịch trình
      tags:
        - Activity
      parameters:
        - name: cruise_day_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Danh sách tour
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/ExcursionResponse'
    """
    excursions = service.list_excursions(cruise_day_id)
    return jsonify(excursion_res.dump(excursions, many=True)), 200


@bp.route("/cruise-days/<int:cruise_day_id>/excursions", methods=["POST"])
def create_excursion(cruise_day_id):
    """
    Tạo tour trên bờ
    ---
    post:
      summary: Tạo chuyến tham quan bờ (UC18)
      tags:
        - Activity
      parameters:
        - name: cruise_day_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ExcursionRequest'
      responses:
        201:
          description: Tạo thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExcursionResponse'
        400:
          description: Dữ liệu không hợp lệ
    """
    data = request.get_json()
    data["cruise_day_id"] = cruise_day_id
    errors = excursion_req.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        excursion = service.create_excursion(excursion_req.load(data))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(excursion_res.dump(excursion)), 201


@bp.route("/excursions/<int:excursion_id>/status", methods=["PUT"])
def update_excursion_status(excursion_id):
    """
    Cập nhật trạng thái tour
    ---
    put:
      summary: Theo dõi trạng thái chuyến tham quan (UC20 - completed/cancelled/delayed)
      tags:
        - Activity
      parameters:
        - name: excursion_id
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
              properties:
                status:
                  type: string
                  enum: [scheduled, completed, cancelled, delayed]
      responses:
        200:
          description: Cập nhật thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExcursionResponse'
        400:
          description: Trạng thái không hợp lệ
        404:
          description: Không tìm thấy tour
    """
    data = request.get_json()
    try:
        excursion = service.update_excursion_status(excursion_id, data.get("status"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not excursion:
        return jsonify({"message": "Excursion not found"}), 404
    return jsonify(excursion_res.dump(excursion)), 200


# ==================== REGISTRATION ====================
@bp.route("/registrations", methods=["POST"])
def register():
    """
    Đăng ký hoạt động/tour
    ---
    post:
      summary: Đăng ký hoạt động/tham quan bờ (UC07/UC08). Áp dụng BR-02 kiểm tra sức chứa.
      tags:
        - Activity
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RegistrationRequest'
      responses:
        201:
          description: Đăng ký thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RegistrationResponse'
        400:
          description: "Đăng ký thất bại (ví dụ đã đạt sức chứa tối đa - MSG01)"
    """
    data = request.get_json()
    errors = registration_req.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        registration = service.register(
            passenger_id=data["passenger_id"],
            activity_id=data.get("activity_id"),
            excursion_id=data.get("excursion_id"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(registration_res.dump(registration)), 201


@bp.route("/registrations/<int:registration_id>/cancel", methods=["PUT"])
def cancel_registration(registration_id):
    """
    Hủy đăng ký
    ---
    put:
      summary: Hủy 1 đăng ký hoạt động/tour
      tags:
        - Activity
      parameters:
        - name: registration_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Hủy thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RegistrationResponse'
        404:
          description: Không tìm thấy đăng ký
    """
    registration = service.cancel_registration(registration_id)
    if not registration:
        return jsonify({"message": "Registration not found"}), 404
    return jsonify(registration_res.dump(registration)), 200


@bp.route("/activities/<int:activity_id>/registrations", methods=["GET"])
def list_activity_registrations(activity_id):
    """
    Danh sách đăng ký của 1 hoạt động
    ---
    get:
      summary: Quản lý danh sách đăng ký hoạt động (UC16)
      tags:
        - Activity
      parameters:
        - name: activity_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Danh sách đăng ký
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/RegistrationResponse'
    """
    registrations = service.list_registrations(activity_id=activity_id)
    return jsonify(registration_res.dump(registrations, many=True)), 200


@bp.route("/excursions/<int:excursion_id>/registrations", methods=["GET"])
def list_excursion_registrations(excursion_id):
    """
    Danh sách đăng ký của 1 tour trên bờ
    ---
    get:
      summary: Quản lý danh sách hành khách đăng ký tour trên bờ (UC19)
      tags:
        - Activity
      parameters:
        - name: excursion_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Danh sách đăng ký
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/RegistrationResponse'
    """
    registrations = service.list_registrations(excursion_id=excursion_id)
    return jsonify(registration_res.dump(registrations, many=True)), 200


@bp.route("/passengers/<int:passenger_id>/registrations", methods=["GET"])
def list_passenger_registrations(passenger_id):
    """
    Danh sách đăng ký của 1 hành khách
    ---
    get:
      summary: Xem các Activity/Excursion mình đã đăng ký (self-service cho Passenger)
      tags:
        - Activity
      parameters:
        - name: passenger_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Danh sách đăng ký của hành khách này
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/RegistrationResponse'
    """
    registrations = service.list_registrations(passenger_id=passenger_id)
    return jsonify(registration_res.dump(registrations, many=True)), 200
