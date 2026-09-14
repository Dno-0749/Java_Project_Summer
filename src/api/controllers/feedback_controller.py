from flask import Blueprint, request, jsonify
from services.feedback_service import FeedbackService
from api.schemas.feedback import FeedbackRequestSchema, FeedbackResponseSchema

bp = Blueprint("feedback", __name__)
service = FeedbackService()

feedback_req = FeedbackRequestSchema()
feedback_res = FeedbackResponseSchema()


@bp.route("/feedback", methods=["POST"])
def create_feedback():
    """
    Gửi đánh giá
    ---
    post:
      summary: Gửi feedback cho Activity/Excursion/Service/Cruise (Passenger tự thực hiện)
      tags:
        - Feedback
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/FeedbackRequest'
      responses:
        201:
          description: Gửi đánh giá thành công
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FeedbackResponse'
        400:
          description: Dữ liệu không hợp lệ (rating phải 1-5, target_type sai)
    """
    data = request.get_json()
    errors = feedback_req.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        fb = service.create(
            passenger_id=data["passenger_id"],
            target_type=data["target_type"],
            rating=data["rating"],
            target_id=data.get("target_id"),
            target_name=data.get("target_name"),
            comment=data.get("comment"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(feedback_res.dump(fb)), 201


@bp.route("/passengers/<int:passenger_id>/feedback", methods=["GET"])
def list_passenger_feedback(passenger_id):
    """
    Đánh giá của tôi
    ---
    get:
      summary: Xem toàn bộ đánh giá đã gửi của 1 hành khách
      tags:
        - Feedback
      parameters:
        - name: passenger_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Danh sách đánh giá
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/FeedbackResponse'
    """
    items = service.list_by_passenger(passenger_id)
    return jsonify(feedback_res.dump(items, many=True)), 200


@bp.route("/feedback", methods=["GET"])
def list_feedback_by_target():
    """
    Đánh giá theo đối tượng
    ---
    get:
      summary: Xem đánh giá theo target_type/target_id (dùng cho Quản lý xem đánh giá tổng hợp)
      tags:
        - Feedback
      parameters:
        - name: target_type
          in: query
          required: true
          schema:
            type: string
        - name: target_id
          in: query
          required: false
          schema:
            type: integer
      responses:
        200:
          description: Danh sách đánh giá
    """
    target_type = request.args.get("target_type")
    target_id = request.args.get("target_id", type=int)
    if not target_type:
        return jsonify({"error": "Thiếu tham số target_type"}), 400
    items = service.list_by_target(target_type, target_id)
    return jsonify(feedback_res.dump(items, many=True)), 200
