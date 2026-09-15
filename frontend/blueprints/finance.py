from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from functools import wraps
import api_client

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")

def finance_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["finance", "admin"]:
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function

@finance_bp.route("/")
@finance_bp.route("/overview")
@login_required
@finance_access
def finance():
    transactions = [
        {"id": "TX-10021", "cabin": "1204", "item": "Spa - Massage 60p", "amount": 1_200_000, "time": "10:22", "staff": "NV POS 02"},
        {"id": "TX-10020", "cabin": "0812", "item": "Wine Tasting", "amount": 850_000, "time": "09:45", "staff": "NV POS 01"},
        {"id": "TX-10019", "cabin": "1501", "item": "Shore Excursion", "amount": 1_500_000, "time": "08:30", "staff": "System"},
        {"id": "TX-10018", "cabin": "1204", "item": "Specialty Dining", "amount": 950_000, "time": "19:10", "staff": "NV POS 03"},
    ]
    return render_template("finance/finance.html", transactions=transactions, page_title="Tài chính & Đối soát")

@finance_bp.route("/passengers")
@login_required
def passengers():
    # Hành khách có thể xem bởi finance, operations, admin
    if current_user.role not in ["finance", "operations", "admin"]:
        return render_template("system_admin/403.html"), 403

    passengers_list = [
        {"id": 1, "name": "Nguyễn Văn A", "cabin": "1204", "card_id": "CR-8821", "checkin": "Đã lên tàu", "balance": 2_150_000},
        {"id": 2, "name": "Trần Thị B", "cabin": "0812", "card_id": "CR-8822", "checkin": "Đã lên tàu", "balance": 850_000},
        {"id": 3, "name": "Lê Hoàng C", "cabin": "1501", "card_id": "CR-8823", "checkin": "Chưa check-in", "balance": 0},
        {"id": 4, "name": "Phạm Minh D", "cabin": "0605", "card_id": "CR-8824", "checkin": "Đã lên tàu", "balance": 3_400_000},
    ]
    return render_template("finance/passengers.html", passengers=passengers_list, page_title="Quản lý Hành khách")


# ==================== THANH TOÁN CUỐI CHUYẾN & XUẤT HÓA ĐƠN (dữ liệu thật) ====================

@finance_bp.route("/settlement")
@login_required
@finance_access
def settlement():
    """UC28/UC29: Xem danh sách tài khoản hành khách để xác nhận thanh toán
    cuối chuyến và xuất hóa đơn - dữ liệu thật từ backend/Supabase."""
    cruise, err = api_client.ensure_demo_cruise()
    if err:
        flash(f"Lỗi kết nối backend: {err}", "danger")
        return render_template("finance/settlement.html", accounts=[], page_title="Thanh toán cuối chuyến")

    passengers, err = api_client.list_passengers(cruise["id"])
    if err:
        flash(f"Lỗi tải danh sách hành khách: {err}", "danger")
        passengers = []

    accounts = []
    for p in passengers or []:
        account, err2 = api_client.get_account(p["id"])
        if err2 or not account:
            continue
        transactions, _ = api_client.list_passenger_transactions(p["id"])
        transactions = transactions or []
        has_pending_or_disputed = any(t["sync_status"] in ("pending_sync", "disputed") for t in transactions)
        accounts.append({
            "account_id": account["id"],
            "passenger_name": p["full_name"],
            "cabin": p.get("cabin_id") or "-",
            "balance": float(account["balance"]),
            "status": account["status"],
            "transaction_count": len(transactions),
            "has_pending_or_disputed": has_pending_or_disputed,
        })

    return render_template("finance/settlement.html", accounts=accounts, page_title="Thanh toán cuối chuyến")


@finance_bp.route("/accounts/<int:account_id>/settle", methods=["POST"])
@login_required
@finance_access
def settle(account_id):
    """UC28: Xác nhận thanh toán cuối chuyến. Áp dụng BR-05 - backend sẽ
    từ chối nếu tài khoản còn giao dịch pending_sync/disputed chưa xử lý."""
    result, err = api_client.settle_account(account_id)
    if err:
        flash(f"Không thể xác nhận thanh toán: {err}", "danger")
    else:
        flash(f"Đã xác nhận thanh toán cuối chuyến cho tài khoản #{account_id}.", "success")
    return redirect(url_for("finance.settlement"))


@finance_bp.route("/accounts/<int:account_id>/invoice", methods=["POST"])
@login_required
@finance_access
def issue_invoice(account_id):
    """UC29: Xuất hóa đơn cuối chuyến (MSG08 nếu bị chặn, MSG09 nếu thành công)."""
    invoice, err = api_client.issue_invoice(account_id)
    if err:
        # Đúng MSG08 trong SRS: "Không thể xuất hóa đơn. Tài khoản còn giao dịch tranh chấp chưa xử lý."
        flash(err, "danger")
        return redirect(url_for("finance.settlement"))

    # Lưu tạm để hiển thị trang hóa đơn (backend chưa có endpoint GET 1 invoice theo id)
    account_name = next(
        (a["passenger_name"] for a in _get_settlement_accounts_cache() if a["account_id"] == account_id),
        "Hành khách"
    )
    session["last_invoice"] = {
        "id": invoice["id"], "account_id": account_id,
        "total_amount": float(invoice["total_amount"]),
        "issued_at": invoice.get("issued_at", ""), "status": invoice["status"],
    }
    flash("Hóa đơn cuối chuyến đã được xuất thành công.", "success")
    return redirect(url_for("finance.invoice_view"))


def _get_settlement_accounts_cache():
    """Helper nhỏ để lấy lại tên hành khách hiển thị trên hóa đơn - tránh
    gọi lại toàn bộ danh sách nếu không cần thiết."""
    cruise, err = api_client.ensure_demo_cruise()
    if err:
        return []
    passengers, err = api_client.list_passengers(cruise["id"])
    if err:
        return []
    result = []
    for p in passengers or []:
        account, err2 = api_client.get_account(p["id"])
        if account:
            result.append({"account_id": account["id"], "passenger_name": p["full_name"]})
    return result


@finance_bp.route("/invoice")
@login_required
@finance_access
def invoice_view():
    """Xem hóa đơn vừa xuất."""
    data = session.pop("last_invoice", None)
    if not data:
        flash("Không có hóa đơn nào để hiển thị.", "warning")
        return redirect(url_for("finance.settlement"))
    return render_template("finance/invoice.html", invoice=data, page_title="Hóa đơn cuối chuyến")
