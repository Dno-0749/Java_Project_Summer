from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields
from services.account_service import AccountService

bp = Blueprint("account", __name__)
service = AccountService()


class AccountResponseSchema(Schema):
    id = fields.Int()
    passenger_id = fields.Int()
    balance = fields.Decimal(as_string=True)
    status = fields.Str()


class TransactionRequestSchema(Schema):
    passenger_id = fields.Int(required=True)
    amount = fields.Decimal(required=True)
    description = fields.Str(required=False)
    staff_id = fields.Int(required=False, allow_none=True)
    local_id = fields.Str(required=False, allow_none=True)


class TransactionResponseSchema(Schema):
    id = fields.Int()
    local_id = fields.Str(allow_none=True)
    onboard_account_id = fields.Int()
    staff_id = fields.Int(allow_none=True)
    amount = fields.Decimal(as_string=True)
    description = fields.Str(allow_none=True)
    sync_status = fields.Str()
    created_at = fields.Raw()
    synced_at = fields.Raw(allow_none=True)


account_res = AccountResponseSchema()
tx_req = TransactionRequestSchema()
tx_res = TransactionResponseSchema()


@bp.route("/transactions", methods=["GET"])
def list_all_transactions():
    """
    Toàn bộ giao dịch gần nhất
    ---
    get:
      summary: Lấy danh sách giao dịch gần nhất (không lọc theo hành khách) - dùng cho màn lịch sử POS
      tags:
        - Account
      responses:
        200:
          description: Danh sách giao dịch
    """
    transactions = service.list_all_transactions()
    return jsonify(tx_res.dump(transactions, many=True)), 200


@bp.route("/passengers/<int:passenger_id>/account", methods=["GET"])
def get_account(passenger_id):
    """
    Xem tài khoản trên tàu
    ---
    get:
      summary: Quản lý tài khoản trên tàu - xem số dư hiện tại (UC26)
      tags:
        - Account
      parameters:
        - name: passenger_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Thông tin tài khoản (tự tạo nếu chưa có - BR-01)
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: integer
                  passenger_id:
                    type: integer
                  balance:
                    type: string
                  status:
                    type: string
    """
    account = service.get_or_create_account(passenger_id)
    return jsonify(account_res.dump(account)), 200


@bp.route("/transactions", methods=["POST"])
def create_transaction():
    """
    Ghi nhận giao dịch (đang có mạng)
    ---
    post:
      summary: Ghi nhận giao dịch dịch vụ + ghi nợ tài khoản (UC21/UC23), dùng khi thiết bị POS đang online
      tags:
        - Account
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [passenger_id, amount]
              properties:
                passenger_id:
                  type: integer
                amount:
                  type: number
                description:
                  type: string
                staff_id:
                  type: integer
                local_id:
                  type: string
                  description: UUID sinh tại thiết bị (khuyến nghị dùng ngay cả khi online)
      responses:
        201:
          description: Ghi nhận thành công
        400:
          description: Dữ liệu không hợp lệ (số tiền phải > 0)
    """
    data = request.get_json()
    errors = tx_req.validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        tx = service.create_transaction(
            passenger_id=data["passenger_id"],
            amount=data["amount"],
            description=data.get("description"),
            staff_id=data.get("staff_id"),
            local_id=data.get("local_id"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(tx_res.dump(tx)), 201


@bp.route("/sync/transactions", methods=["POST"])
def sync_transactions():
    """
    Đồng bộ batch giao dịch offline
    ---
    post:
      summary: "Đồng bộ batch giao dịch lưu offline tại thiết bị POS (UC25). Mỗi item bắt buộc có local_id (BR-04) để chống ghi trùng khi gửi lại."
      tags:
        - Account
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [passenger_id, transactions]
              properties:
                passenger_id:
                  type: integer
                staff_id:
                  type: integer
                transactions:
                  type: array
                  items:
                    type: object
                    properties:
                      local_id:
                        type: string
                      amount:
                        type: number
                      description:
                        type: string
      responses:
        200:
          description: "Kết quả đồng bộ từng item (synced / already_synced / sync_failed - MSG06/MSG07)"
    """
    data = request.get_json()
    passenger_id = data.get("passenger_id")
    transactions = data.get("transactions")
    if not passenger_id or not transactions:
        return jsonify({"error": "Thiếu passenger_id hoặc transactions"}), 400

    results = service.sync_offline_transactions(
        passenger_id=passenger_id,
        transactions=transactions,
        staff_id=data.get("staff_id"),
    )
    return jsonify({"results": results}), 200


@bp.route("/transactions/<int:transaction_id>/refund", methods=["PUT"])
def refund_transaction(transaction_id):
    """
    Hoàn tiền giao dịch
    ---
    put:
      summary: Hủy/hoàn tiền giao dịch (UC24)
      tags:
        - Account
      parameters:
        - name: transaction_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Hoàn tiền thành công
        404:
          description: Không tìm thấy giao dịch
    """
    try:
        tx = service.refund(transaction_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify(tx_res.dump(tx)), 200


@bp.route("/passengers/<int:passenger_id>/transactions", methods=["GET"])
def list_transactions(passenger_id):
    """
    Hóa đơn tạm tính
    ---
    get:
      summary: Xem chi phí phát sinh (hóa đơn tạm tính) (UC10)
      tags:
        - Account
      parameters:
        - name: passenger_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Danh sách giao dịch
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
    """
    transactions = service.list_transactions(passenger_id)
    return jsonify(tx_res.dump(transactions, many=True)), 200
