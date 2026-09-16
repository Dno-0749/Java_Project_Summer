from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import wraps

operations_bp = Blueprint("operations", __name__, url_prefix="/operations")

def operations_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["operations", "admin"]:
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function

@operations_bp.route("/dashboard")
@login_required
@operations_access
def dashboard():
    stats = {
        "passengers": 1248,
        "activities_today": 18,
        "excursions_today": 6,
        "revenue_today": 245_800_000,
        "checkins_today": 892,
        "pending_registrations": 47,
    }
    recent_activities = [
        {"time": "09:15", "event": "Hành khách check-in Yoga Class", "user": "Nguyễn Văn A"},
        {"time": "09:02", "event": "Đăng ký mới: Shore Excursion Phú Quốc", "user": "Trần Thị B"},
        {"time": "08:45", "event": "POS ghi nhận giao dịch Spa", "user": "NV POS 03"},
        {"time": "08:30", "event": "Cập nhật lịch trình ngày 3", "user": "Điều phối"},
        {"time": "08:10", "event": "Xuất hóa đơn cuối chuyến phòng 1204", "user": "Tài chính"},
    ]
    return render_template(
        "operations/dashboard.html",
        stats=stats,
        recent_activities=recent_activities,
        page_title="Dashboard Vận hành"
    )
