from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")

CHECKIN_LOGS = []

PASSENGERS = [
    {"id": 1, "name": "Nguyễn Văn A", "cabin": "1204", "card_id": "CR-8821", "checkin": "Chưa check-in", "balance": 2_150_000, "ticket_paid": True},
    {"id": 2, "name": "Trần Thị B", "cabin": "0812", "card_id": "CR-8822", "checkin": "Chưa check-in", "balance": 850_000, "ticket_paid": True},
    {"id": 3, "name": "Lê Hoàng C", "cabin": "1501", "card_id": "CR-8823", "checkin": "Chưa check-in", "balance": 0, "ticket_paid": True},
    {"id": 4, "name": "Phạm Minh D", "cabin": "0605", "card_id": "CR-8824", "checkin": "Đã lên tàu", "balance": 3_400_000, "ticket_paid": True},
]


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

@finance_bp.route("/bookings")
@login_required
@finance_access
def bookings():
    bookings_list = [
        {"id": "BK-9001", "guest": "Nguyễn Văn A", "cabin": "1204", "package": "Premium Balcony", "status": "Confirmed", "amount": 18000000},
        {"id": "BK-9002", "guest": "Trần Thị B", "cabin": "0812", "package": "Ocean View", "status": "Pending", "amount": 13500000},
        {"id": "BK-9003", "guest": "Lê Hoàng C", "cabin": "1501", "package": "Family Room", "status": "Confirmed", "amount": 22000000},
    ]
    return render_template("finance/bookings.html", bookings=bookings_list, page_title="Quản lý Booking")

@finance_bp.route("/cabins")
@login_required
@finance_access
def cabins():
    cabins_list = [
        {"number": "1204", "type": "Balcony", "guest": "Nguyễn Văn A", "status": "Occupied", "rate": 4500000},
        {"number": "0812", "type": "Ocean View", "guest": "Trần Thị B", "status": "Occupied", "rate": 3800000},
        {"number": "1501", "type": "Family", "guest": "Lê Hoàng C", "status": "Reserved", "rate": 5200000},
    ]
    return render_template("finance/cabins.html", cabins=cabins_list, page_title="Quản lý Cabin")

@finance_bp.route("/services")
@login_required
@finance_access
def services():
    services_list = [
        {"name": "Wine Tasting", "fee_type": "Có tính phí", "price": 850000, "status": "Available"},
        {"name": "Yoga buổi sáng", "fee_type": "Miễn phí", "price": 0, "status": "Available"},
        {"name": "Spa - Massage 60p", "fee_type": "Có tính phí", "price": 1200000, "status": "Available"},
    ]
    return render_template("finance/services.html", services=services_list, page_title="Dịch vụ miễn phí & có phí")

@finance_bp.route("/expenses")
@login_required
@finance_access
def expenses():
    expenses_list = [
        {"id": "EXP-001", "guest": "Nguyễn Văn A", "item": "Shore Excursion", "amount": 1500000, "status": "Draft"},
        {"id": "EXP-002", "guest": "Trần Thị B", "item": "Dining", "amount": 950000, "status": "Settlement"},
        {"id": "EXP-003", "guest": "Lê Hoàng C", "item": "Spa", "amount": 1200000, "status": "Pending"},
    ]
    return render_template("finance/expenses.html", expenses=expenses_list, page_title="Khoản chi tiêu phát sinh")

@finance_bp.route("/feedback")
@login_required
@finance_access
def feedback():
    feedback_list = [
        {"guest": "Nguyễn Văn A", "subject": "Tour bờ", "rating": 5, "message": "Rất hài lòng"},
        {"guest": "Trần Thị B", "subject": "Dịch vụ", "rating": 4, "message": "Cần cập nhật thêm"},
    ]
    return render_template("finance/feedback.html", feedback=feedback_list, page_title="Phản hồi sau chuyến")

@finance_bp.route("/checkin", methods=["GET", "POST"])
@login_required
@finance_access
def checkin():
    pending_guests = [p for p in PASSENGERS if p.get("ticket_paid") and p.get("checkin") != "Đã lên tàu"]

    if request.method == "POST":
        guest_id = request.form.get("guest_id", "")
        method = request.form.get("method", "card")
        token = request.form.get("token", "")
        guest = next((p for p in PASSENGERS if str(p["id"]) == str(guest_id)), None)

        if guest:
            guest["checkin"] = "Đã lên tàu"
            guest["card_id"] = token or guest.get("card_id", "")

        CHECKIN_LOGS.append({
            "guest_name": guest["name"] if guest else request.form.get("guest_name", ""),
            "card_id": token or request.form.get("card_id", ""),
            "cabin": guest["cabin"] if guest else request.form.get("cabin", ""),
            "method": method,
        })

        flash("Check-in đã được ghi nhận.", "success")
        return redirect(url_for("finance.checkin"))

    return render_template(
        "finance/checkin.html",
        checkin_logs=CHECKIN_LOGS,
        passengers=pending_guests,
        page_title="Check-in hành khách",
    )
