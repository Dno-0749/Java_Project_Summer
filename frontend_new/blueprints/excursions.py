from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

import os
import sys

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from supabase_client import get_supabase_client

excursions_bp = Blueprint("excursions", __name__, url_prefix="/excursions")

EXCURSION_ITEMS = [
    {"id": 1, "name": "Tour Phú Quốc - Hòn Thơm", "date": "2026-09-12", "capacity": 80, "registered": 72, "price": 1500000, "status": "Còn chỗ"},
    {"id": 2, "name": "Lặn ngắm san hô Cát Bà", "date": "2026-09-11", "capacity": 30, "registered": 30, "price": 950000, "status": "Hết chỗ"},
    {"id": 3, "name": "City Tour Nha Trang", "date": "2026-08-21", "capacity": 100, "registered": 88, "price": 600000, "status": "Đã kết thúc"},
]


def excursion_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["activity_manager", "operations", "admin"]:
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function


def get_excursion_by_id(excursion_id):
    response = get_supabase_client().table("shore_excursions").select("*").eq("id", excursion_id).limit(1).execute()
    row = response.data[0] if response.data else None
    return _normalise_excursion(row) if row else None


def _normalise_excursion(row):
    return {
        "id": row.get("id"),
        "name": row.get("name") or row.get("title") or "Tour bờ",
        "date": row.get("date") or row.get("gathering_time") or row.get("start_date") or "-",
        "capacity": int(row.get("capacity") or 0),
        "registered": int(row.get("registered") or row.get("participants") or 0),
        "price": int(row.get("price") or 0),
        "status": row.get("status") or "Còn chỗ",
        "_source": "supabase",
    }


def _live_excursions():
    response = get_supabase_client().table("shore_excursions").select("*").limit(200).execute()
    rows = response.data if hasattr(response, "data") and response.data else []

    excursions = []
    for row in rows:
        excursions.append(_normalise_excursion(row))
    return excursions


def _excursion_payload(form):
    return {
        "name": form.get("name", "").strip(),
        "gathering_time": f"{form.get('date', '').strip()} 08:00:00",
        "capacity": int(form.get("capacity", "0") or 0),
        "price": int(form.get("price", "0") or 0),
        "status": form.get("status", "Còn chỗ").strip(),
    }


def _with_cruise_day(payload):
    response = get_supabase_client().table("cruise_days").select("id").limit(1).execute()
    if not response.data:
        raise RuntimeError("Supabase chưa có cruise_days để gắn tour bờ.")
    return {"cruise_day_id": response.data[0]["id"], **payload}


@excursions_bp.route("/")
@login_required
@excursion_access
def excursions():
    live_excursions = _live_excursions()
    return render_template(
        "excursions/excursions.html",
        excursions=live_excursions,
        page_title="Tham quan bờ",
    )


@excursions_bp.route("/new", methods=["GET", "POST"])
@login_required
@excursion_access
def create_excursion():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        date = request.form.get("date", "").strip()
        capacity = request.form.get("capacity", "0").strip()
        price = request.form.get("price", "0").strip()
        status = request.form.get("status", "Còn chỗ").strip()

        if not name or not date:
            flash("Vui lòng nhập tên tour và ngày khởi hành.", "danger")
            return redirect(url_for("excursions.create_excursion"))

        payload = _excursion_payload(request.form)
        try:
            get_supabase_client().table("shore_excursions").insert(_with_cruise_day(payload)).execute()
            flash("Đã tạo tour bờ mới trên Supabase.", "success")
        except Exception as error:
            flash(f"Không thể lưu tour vào Supabase: {error}", "danger")
        return redirect(url_for("excursions.excursions"))

    return render_template("excursions/new_excursion.html", page_title="Tạo tour bờ mới")


@excursions_bp.route("/<excursion_id>/detail")
@login_required
@excursion_access
def excursion_detail(excursion_id):
    excursion = get_excursion_by_id(excursion_id) or next((item for item in _live_excursions() if item["id"] == excursion_id), None)
    if not excursion:
        flash("Không tìm thấy tour bờ.", "danger")
        return redirect(url_for("excursions.excursions"))
    return render_template("excursions/excursion_detail.html", excursion=excursion, page_title="Chi tiết tour bờ")


@excursions_bp.route("/<excursion_id>/edit", methods=["GET", "POST"])
@login_required
@excursion_access
def edit_excursion(excursion_id):
    excursion = get_excursion_by_id(excursion_id) or next((item for item in _live_excursions() if item["id"] == excursion_id), None)
    if not excursion:
        flash("Không tìm thấy tour bờ.", "danger")
        return redirect(url_for("excursions.excursions"))

    if request.method == "POST":
        payload = _excursion_payload(request.form)
        try:
            get_supabase_client().table("shore_excursions").update(payload).eq("id", excursion_id).execute()
            flash("Đã cập nhật tour bờ trên Supabase.", "success")
        except Exception:
            excursion.update(payload)
            flash("Chưa cập nhật được Supabase, thay đổi chỉ có hiệu lực trong phiên hiện tại.", "warning")
        return redirect(url_for("excursions.excursion_detail", excursion_id=excursion_id))

    return render_template("excursions/edit_excursion.html", excursion=excursion, page_title="Sửa tour bờ")
