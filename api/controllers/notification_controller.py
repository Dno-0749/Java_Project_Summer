from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields
from services.notification_service import NotificationService

bp = Blueprint("notification", __name__)
service = NotificationService()


class NotificationResponseSchema(Schema):
    id = fields.Int()
    passenger_id = fields.Int(allow_none=True)
    cruise_id = fields.Int(allow_none=True)
    title = fields.Str()
    content = fields.Str(allow_none=True)
    category = fields.Str()
    priority = fields.Str()
    is_read = fields.Bool()
    created_at = fields.Raw()


notification_res = NotificationResponseSchema()


@bp.route("/notifications", methods=["POST"])
def create_notification():
    """
    Tạo thông báo
    ---
    post:
      summary: Tạo thông báo (dùng bởi hệ thống/điều phối khi có thay đổi lịch trình)
      tags:
        - Notification
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [title]
              properties:
                title:
                  type: string
                content:
                  type: string
                passenger_id:
                  type: integer
                  description: "Để trống nếu là thông báo chung cho cả cruise"
                cruise_id:
                  type: integer
                category:
                  type: string
                  enum: [itinerary, activity, registration, transaction, general]
                priority:
                  type: string
                  enum: [normal, high]
      responses:
        201:
          description: Tạo thành công
        400:
          description: Thiếu title
    """
    data = request.get_json()
    try:
        n = service.create(
            title=data.get("title"), content=data.get("content"),
            passenger_id=data.get("passenger_id"), cruise_id=data.get("cruise_id"),
            category=data.get("category", "general"), priority=data.get("priority", "normal"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(notification_res.dump(n)), 201


@bp.route("/passengers/<int:passenger_id>/notifications", methods=["GET"])
def list_passenger_notifications(passenger_id):
    """
    Thông báo của tôi
    ---
    get:
      summary: Xem thông báo của 1 hành khách (bao gồm cả thông báo chung của cruise)
      tags:
        - Notification
      parameters:
        - name: passenger_id
          in: path
          required: true
          schema:
            type: integer
        - name: cruise_id
          in: query
          required: false
          schema:
            type: integer
      responses:
        200:
          description: Danh sách thông báo
    """
    cruise_id = request.args.get("cruise_id", type=int)
    items = service.list_for_passenger(passenger_id, cruise_id)
    return jsonify(notification_res.dump(items, many=True)), 200


@bp.route("/notifications/<int:notification_id>/read", methods=["PUT"])
def mark_read(notification_id):
    """
    Đánh dấu đã đọc
    ---
    put:
      summary: Đánh dấu 1 thông báo đã đọc
      tags:
        - Notification
      parameters:
        - name: notification_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Đã đánh dấu đã đọc
        404:
          description: Không tìm thấy
    """
    n = service.mark_read(notification_id)
    if not n:
        return jsonify({"message": "Notification not found"}), 404
    return jsonify(notification_res.dump(n)), 200
