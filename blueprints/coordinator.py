from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import wraps

coordinator_bp = Blueprint("coordinator", __name__, url_prefix="/coordinator")

def coordinator_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["coordinator", "operations", "admin"]:
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function

@coordinator_bp.route("/")
@coordinator_bp.route("/itinerary")
@login_required
@coordinator_access
def itinerary():
    tours = [
        {
            "id": 1,
            "name": "Hạ Long - Cát Bà 5 ngày",
            "start_date": "2026-09-10",
            "end_date": "2026-09-14",
            "status": "Đang diễn ra",
            "passengers": 420,
            "ports": ["Hạ Long", "Cát Bà", "Lan Hạ"],
        },
        {
            "id": 2,
            "name": "Phú Quốc - Nam Du 4 ngày",
            "start_date": "2026-09-18",
            "end_date": "2026-09-21",
            "status": "Sắp khởi hành",
            "passengers": 380,
            "ports": ["Phú Quốc", "Nam Du"],
        },
        {
            "id": 3,
            "name": "Nha Trang - Bình Hưng 3 ngày",
            "start_date": "2026-08-20",
            "end_date": "2026-08-22",
            "status": "Đã kết thúc",
            "passengers": 310,
            "ports": ["Nha Trang", "Bình Hưng"],
        },
    ]
    return render_template("coordinator/itinerary.html", tours=tours, page_title="Quản lý Lịch trình")
