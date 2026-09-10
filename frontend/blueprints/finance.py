from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import wraps

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
