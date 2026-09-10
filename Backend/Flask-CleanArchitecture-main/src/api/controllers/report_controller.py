from flask import Blueprint, request, jsonify
from services.report_service import ReportService
from api.schemas.report import InvoiceResponseSchema

bp = Blueprint("report", __name__)
service = ReportService()
invoice_res = InvoiceResponseSchema()


@bp.route("/accounts/<int:account_id>/reconcile", methods=["POST"])
def reconcile(account_id):
    """
    Đối soát giao dịch POS
    ---
    post:
      summary: Đối soát toàn bộ giao dịch 'synced' của 1 tài khoản, chuyển thành 'reconciled' (UC27)
      tags:
        - Report
      parameters:
        - name: account_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Kết quả đối soát
          content:
            application/json:
              schema:
                type: object
                properties:
                  account_id:
                    type: integer
                  reconciled_count:
                    type: integer
        400:
          description: Không tìm thấy tài khoản
    """
    try:
        result = service.reconcile(account_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(result), 200


@bp.route("/transactions/<int:transaction_id>/dispute", methods=["PUT"])
def mark_disputed(transaction_id):
    """
    Đánh dấu tranh chấp
    ---
    put:
      summary: Đánh dấu 1 giao dịch là tranh chấp (dispute), chặn xuất hóa đơn cho tới khi xử lý
      tags:
        - Report
      parameters:
        - name: transaction_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Đã đánh dấu tranh chấp
        404:
          description: Không tìm thấy giao dịch
    """
    try:
        tx = service.mark_disputed(transaction_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify({"id": tx.id, "sync_status": tx.sync_status}), 200


@bp.route("/accounts/<int:account_id>/settle", methods=["POST"])
def settle(account_id):
    """
    Xác nhận thanh toán cuối chuyến
    ---
    post:
      summary: Xác nhận thanh toán cuối chuyến (UC28). Áp dụng BR-05.
      tags:
        - Report
      parameters:
        - name: account_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Xác nhận thành công, tài khoản chuyển trạng thái 'settled'
        400:
          description: "Còn giao dịch tranh chấp/chưa đồng bộ, không thể xác nhận"
    """
    try:
        account = service.settle_final_payment(account_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"id": account.id, "status": account.status}), 200


@bp.route("/accounts/<int:account_id>/invoice", methods=["POST"])
def issue_invoice(account_id):
    """
    Xuất hóa đơn cuối chuyến
    ---
    post:
      summary: Xuất hóa đơn tổng hợp cho hành khách (UC29). Áp dụng BR-05 (MSG08/MSG09).
      tags:
        - Report
      parameters:
        - name: account_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        201:
          description: "Xuất hóa đơn thành công (MSG09)"
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InvoiceResponse'
        400:
          description: "Không thể xuất hóa đơn - còn giao dịch tranh chấp chưa xử lý (MSG08)"
    """
    try:
        invoice = service.issue_invoice(account_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(invoice_res.dump(invoice)), 201


@bp.route("/cruises/<int:cruise_id>/dashboard", methods=["GET"])
def dashboard(cruise_id):
    """
    Dashboard vận hành
    ---
    get:
      summary: Xem dashboard vận hành - tỷ lệ tham gia từng hoạt động (UC30)
      tags:
        - Report
      parameters:
        - name: cruise_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Danh sách hoạt động kèm số liệu đăng ký/check-in
    """
    result = service.activity_participation(cruise_id)
    return jsonify(result), 200


@bp.route("/cruise-days/<int:cruise_day_id>/late-return-risk", methods=["GET"])
def late_return_risk(cruise_day_id):
    """
    Giám sát rủi ro quay lại tàu muộn
    ---
    get:
      summary: Danh sách hành khách đã đăng ký tour bờ nhưng chưa check-in quay lại tàu (UC31)
      tags:
        - Report
      parameters:
        - name: cruise_day_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Danh sách hành khách có rủi ro trễ giờ
    """
    result = service.late_return_risk(cruise_day_id)
    return jsonify(result), 200


@bp.route("/cruises/<int:cruise_id>/operations-summary", methods=["GET"])
def operations_summary(cruise_id):
    """
    Báo cáo vận hành sau chuyến đi
    ---
    get:
      summary: Báo cáo vận hành tổng hợp sau chuyến đi (UC32)
      tags:
        - Report
      parameters:
        - name: cruise_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        200:
          description: Báo cáo tổng hợp (tỷ lệ đăng ký, check-in toàn chuyến)
    """
    result = service.operations_summary(cruise_id)
    return jsonify(result), 200
