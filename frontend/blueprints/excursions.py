from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

excursions_bp = Blueprint("excursions", __name__, url_prefix="/excursions")
EXCURSION_REGISTRATIONS = []

def excursion_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["activity_manager", "operations", "admin"]:
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function

@excursions_bp.route("/")
@login_required
@excursion_access
def excursions():
    excursions_list = [
        {"id": 1, "name": "Tour Phú Quốc - Hòn Thơm", "date": "2026-09-12", "capacity": 80, "registered": 72, "price": 1500000, "status": "Còn chỗ"},
        {"id": 2, "name": "Lặn ngắm san hô Cát Bà", "date": "2026-09-11", "capacity": 30, "registered": 30, "price": 950000, "status": "Hết chỗ"},
        {"id": 3, "name": "City Tour Nha Trang", "date": "2026-08-21", "capacity": 100, "registered": 88, "price": 600000, "status": "Đã kết thúc"},
    ]
    return render_template("excursions/excursions.html", excursions=excursions_list, page_title="Tham quan bờ")

@excursions_bp.route("/register", methods=["GET", "POST"])
@login_required
@excursion_access
def register_excursion():
    if request.method == "POST":
        tour_name = request.form.get("tour_name", "Tour mới")
        date = request.form.get("date", "")
        capacity = int(request.form.get("capacity", 0) or 0)
        price = int(request.form.get("price", 0) or 0)
        status = request.form.get("status", "Còn chỗ")
        note = request.form.get("note", "")

        new_tour = {
            "id": len(EXCURSION_REGISTRATIONS) + 1,
            "name": tour_name,
            "date": date,
            "capacity": capacity,
            "registered": 0,
            "price": price,
            "status": status,
            "note": note,
        }
        EXCURSION_REGISTRATIONS.append(new_tour)
        flash("Tour tham quan mới đã được tạo.", "success")
        return redirect(url_for("excursions.excursions"))

    return render_template("excursions/register_excursion.html", page_title="Tạo tour tham quan mới")
