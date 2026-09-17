from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields
from services.checkin_service import CheckinService

bp = Blueprint("checkin", __name__)
service = CheckinService()


class CheckinRequestSchema(Schema):
    registration_id = fields.Int(required=True)
    method = fields.Str(required=True)


class CheckinResponseSchema(Schema):
    id = fields.Int()
    registration_id = fields.Int()
    method = fields.Str()
    checked_in_at = fields.Raw()


checkin_req = CheckinRequestSchema()
checkin_res = CheckinResponseSchema()


@bp.route("/checkins", methods=["POST"])
def checkin():
    """
    Check-in hoạt động
    ---
    post:
      summary: Check-in bằng QR/thẻ/RFID-NFC (UC09/UC17)
      tags:
        - Checkin
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [registration_id, method]
              properties:
                registration_id:
                  type: integer
                method:
                  type: string
                  enum: [qr, card, rfid]
      responses:
        201:
          description: "Check-in thành công (MSG04)"
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: integer
                  registration_id:
                    type: integer
                  method:
                    type: string
                  checked_in_at: {}
        400:
          description: "Mã xác thực không hợp lệ hoặc chưa đăng ký hoạt động này (MSG03)"
    """
    data = request.get_json()
    errors = checkin_req.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        result = service.checkin(data["registration_id"], data["method"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(checkin_res.dump(result)), 201
