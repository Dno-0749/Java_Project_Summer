from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields
from services.booking_service import BookingService

bp = Blueprint("booking", __name__)
service = BookingService()


class BookingResponseSchema(Schema):
    id = fields.Int()
    cruise_id = fields.Int(allow_none=True)
    cabin_id = fields.Int(allow_none=True)
    booking_reference = fields.Str(allow_none=True)
    ship_name = fields.Str(allow_none=True)
    customer_name = fields.Str(allow_none=True)
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
    status = fields.Str()
    created_at = fields.Raw()
    updated_at = fields.Raw()


booking_res = BookingResponseSchema()


@bp.route("/bookings", methods=["GET"])
def list_bookings():
    """
    Danh sách booking
    ---
    get:
      summary: Quản lý Booking - dùng cho Điều phối lịch trình
      tags:
        - Booking
      responses:
        200:
          description: Danh sách booking
    """
    bookings = service.list_bookings()
    return jsonify(booking_res.dump(bookings, many=True)), 200


@bp.route("/bookings", methods=["POST"])
def create_booking():
    """
    Tạo booking
    ---
    post:
      summary: Tạo booking mới
      tags:
        - Booking
      responses:
        201:
          description: Tạo thành công
        400:
          description: Dữ liệu không hợp lệ
    """
    data = request.get_json() or {}
    try:
        booking = service.create_booking(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(booking_res.dump(booking)), 201


@bp.route("/bookings/<int:booking_id>", methods=["PUT"])
def update_booking(booking_id):
    """
    Cập nhật booking
    ---
    put:
      summary: Cập nhật thông tin booking
      tags:
        - Booking
      parameters:
        - name: booking_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Cập nhật thành công
        404:
          description: Không tìm thấy booking
    """
    data = request.get_json() or {}
    try:
        booking = service.update_booking(booking_id, data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not booking:
        return jsonify({"error": "Không tìm thấy booking"}), 404
    return jsonify(booking_res.dump(booking)), 200


@bp.route("/bookings/<int:booking_id>/status", methods=["PATCH"])
def update_booking_status(booking_id):
    """
    Cập nhật trạng thái booking
    ---
    patch:
      summary: Cập nhật riêng trạng thái booking (pending/confirmed/cancelled/completed)
      tags:
        - Booking
      parameters:
        - name: booking_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Cập nhật thành công
        400:
          description: Trạng thái không hợp lệ
        404:
          description: Không tìm thấy booking
    """
    data = request.get_json() or {}
    try:
        booking = service.update_status(booking_id, data.get("status"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not booking:
        return jsonify({"error": "Không tìm thấy booking"}), 404
    return jsonify(booking_res.dump(booking)), 200


@bp.route("/bookings/<int:booking_id>", methods=["DELETE"])
def delete_booking(booking_id):
    """
    Xóa booking
    ---
    delete:
      summary: Xóa booking
      tags:
        - Booking
      parameters:
        - name: booking_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Xóa thành công
        404:
          description: Không tìm thấy booking
    """
    if not service.delete_booking(booking_id):
        return jsonify({"error": "Không tìm thấy booking"}), 404
    return jsonify({"message": "Đã xóa booking"}), 200
