from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

coordinator_bp = Blueprint("coordinator", __name__, url_prefix="/coordinator")

TOURS = [
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


def coordinator_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["coordinator", "operations", "admin"]:
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function


def get_tour_by_id(tour_id):
    return next((tour for tour in TOURS if tour["id"] == tour_id), None)


@coordinator_bp.route("/")
@coordinator_bp.route("/itinerary")
@login_required
@coordinator_access
def itinerary():
    return render_template("coordinator/itinerary.html", tours=TOURS, page_title="Quản lý Lịch trình")


@coordinator_bp.route("/itinerary/new", methods=["GET", "POST"])
@login_required
@coordinator_access
def create_tour():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        ports_value = request.form.get("ports", "").strip()
        status = request.form.get("status", "Sắp khởi hành").strip()

        if not name or not start_date or not end_date:
            flash("Vui lòng nhập đầy đủ tên, ngày bắt đầu và ngày kết thúc của tour.", "danger")
            return redirect(url_for("coordinator.create_tour"))

        new_tour = {
            "id": max((tour["id"] for tour in TOURS), default=0) + 1,
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
            "status": status or "Sắp khởi hành",
            "passengers": 0,
            "ports": [port.strip() for port in ports_value.split("\n") if port.strip()],
        }
        TOURS.insert(0, new_tour)
        flash("Đã tạo tour mới thành công.", "success")
        return redirect(url_for("coordinator.itinerary"))

    return render_template("coordinator/new_tour.html", page_title="Tạo tour mới")


@coordinator_bp.route("/itinerary/<int:tour_id>/detail")
@login_required
@coordinator_access
def tour_detail(tour_id):
    tour = get_tour_by_id(tour_id)
    if not tour:
        flash("Không tìm thấy tour.", "danger")
        return redirect(url_for("coordinator.itinerary"))
    return render_template("coordinator/tour_detail.html", tour=tour, page_title="Chi tiết tour")


@coordinator_bp.route("/itinerary/<int:tour_id>/ports", methods=["GET", "POST"])
@login_required
@coordinator_access
def edit_ports(tour_id):
    tour = get_tour_by_id(tour_id)
    if not tour:
        flash("Không tìm thấy tour.", "danger")
        return redirect(url_for("coordinator.itinerary"))

    if request.method == "POST":
        ports_value = request.form.get("ports", "").strip()
        tour["ports"] = [port.strip() for port in ports_value.split("\n") if port.strip()]
        flash("Đã cập nhật danh sách cảng của tour.", "success")
        return redirect(url_for("coordinator.tour_detail", tour_id=tour_id))

    return render_template("coordinator/edit_ports.html", tour=tour, page_title="Sửa cảng tour")
