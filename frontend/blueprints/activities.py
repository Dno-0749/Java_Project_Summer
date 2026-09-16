from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

import os
import sys
from datetime import datetime

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from supabase_client import get_supabase_client

activities_bp = Blueprint("activities", __name__, url_prefix="/activities")

ACTIVITY_ITEMS = [
    {"id": 1, "name": "Yoga buổi sáng", "location": "Sundeck", "time": "06:30 - 07:30", "capacity": 40, "registered": 35, "price": 0, "type": "Miễn phí"},
    {"id": 2, "name": "Wine Tasting", "location": "Sky Lounge", "time": "16:00 - 17:30", "capacity": 25, "registered": 25, "price": 850000, "type": "Trả phí"},
    {"id": 3, "name": "Live Music Night", "location": "Main Stage", "time": "20:00 - 22:00", "capacity": 200, "registered": 178, "price": 0, "type": "Miễn phí"},
    {"id": 4, "name": "Cooking Class", "location": "Culinary Studio", "time": "10:00 - 12:00", "capacity": 15, "registered": 12, "price": 1200000, "type": "Trả phí"},
    {"id": 5, "name": "Kids Club", "location": "Kids Zone", "time": "09:00 - 11:00", "capacity": 30, "registered": 22, "price": 0, "type": "Miễn phí"},
]


def activity_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["activity_manager", "operations", "admin"]:
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function


def get_activity_by_id(activity_id):
    response = get_supabase_client().table("activities").select("*").eq("id", activity_id).limit(1).execute()
    row = response.data[0] if response.data else None
    return _normalise_activity(row) if row else None


def _normalise_activity(row):
    start_time = row.get("start_time") or ""
    end_time = row.get("end_time") or ""
    time_slot = f"{start_time} - {end_time}".strip(" -") or row.get("time") or "-"
    return {
        "id": row.get("id"),
        "cruise_day_id": row.get("cruise_day_id"),
        "ship_area_id": row.get("ship_area_id"),
        "name": row.get("name") or row.get("title") or "Hoạt động",
        "location": row.get("location") or row.get("ship_area_id") or "-",
        "time": time_slot,
        "capacity": int(row.get("capacity") or 0),
        "registered": int(row.get("registered") or row.get("participants") or 0),
        "price": int(row.get("fee") or row.get("price") or 0),
        "type": "Miễn phí" if row.get("is_included_in_package") else (row.get("type") or "Trả phí"),
        "status": row.get("status") or "active",
        "_source": "supabase",
    }


def _live_activities():
    response = get_supabase_client().table("activities").select("*").limit(200).execute()
    rows = response.data if hasattr(response, "data") and response.data else []

    activities = []
    for row in rows:
        capacity = int(row.get("capacity") or 0)
        activities.append(_normalise_activity(row))
    return activities


def _live_ship_areas():
    response = get_supabase_client().table("ship_areas").select("*").limit(200).execute()
    return response.data if hasattr(response, "data") and response.data else []


def _cruise_day(cruise_day_id=None):
    query = get_supabase_client().table("cruise_days").select("id,date,day_number")
    if cruise_day_id:
        query = query.eq("id", cruise_day_id)
    response = query.limit(1).execute()
    return response.data[0] if response.data else None


def _activity_payload(form, cruise_day=None):
    time_parts = form.get("time", "").strip().split("-")
    start_time = time_parts[0].strip() if time_parts else ""
    end_time = time_parts[1].strip() if len(time_parts) > 1 else None
    payload = {
        "name": form.get("name", "").strip(),
        "capacity": int(form.get("capacity", "0") or 0),
        "fee": int(form.get("price", "0") or 0),
        "is_included_in_package": form.get("type", "Miễn phí") == "Miễn phí",
        "status": "scheduled",
    }
    activity_date = (cruise_day or {}).get("date")
    if activity_date and start_time:
        payload["start_time"] = datetime.fromisoformat(
            f"{activity_date}T{start_time}:00+00:00"
        ).isoformat()
    if activity_date and end_time:
        payload["end_time"] = datetime.fromisoformat(
            f"{activity_date}T{end_time}:00+00:00"
        ).isoformat()

    ship_area_id = form.get("ship_area_id", "").strip()
    if ship_area_id:
        payload["ship_area_id"] = int(ship_area_id)
    return payload


def _with_cruise_day(payload):
    cruise_day = _cruise_day()
    if not cruise_day:
        raise RuntimeError("Supabase chưa có cruise_days để gắn hoạt động.")
    return {"cruise_day_id": cruise_day["id"], **payload}


@activities_bp.route("/")
@activities_bp.route("/list")
@login_required
@activity_access
def activities():
    live_activities = _live_activities()
    return render_template(
        "activities/activities.html",
        activities=live_activities,
        page_title="Quản lý Hoạt động trên tàu",
    )


@activities_bp.route("/new", methods=["GET", "POST"])
@login_required
@activity_access
def create_activity():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        ship_area_id = request.form.get("ship_area_id", "").strip()
        time_slot = request.form.get("time", "").strip()
        capacity = request.form.get("capacity", "0").strip()

        errors = []
        if not name:
            errors.append("Tên hoạt động")
        if not time_slot:
            errors.append("Khung giờ")
        if errors:
            flash(f"Vui lòng nhập: {', '.join(errors)}.", "danger")
            return render_template(
                "activities/new_activity.html",
                ship_areas=_live_ship_areas(),
                page_title="Thêm hoạt động mới",
            )

        try:
            capacity_value = int(capacity)
            if capacity_value < 1:
                raise ValueError
        except (TypeError, ValueError):
            flash("Sức chứa phải là số nguyên lớn hơn 0.", "danger")
            return render_template(
                "activities/new_activity.html",
                ship_areas=_live_ship_areas(),
                page_title="Thêm hoạt động mới",
            )

        try:
            cruise_day = _cruise_day()
            if not cruise_day:
                raise RuntimeError("Chưa có ngày chuyến trong bảng cruise_days.")
            payload = _activity_payload(request.form, cruise_day)
            get_supabase_client().table("activities").insert(_with_cruise_day(payload)).execute()
            flash("Đã tạo hoạt động mới trên Supabase.", "success")
        except Exception as error:
            flash(f"Không thể lưu hoạt động vào Supabase: {error}", "danger")
            return render_template(
                "activities/new_activity.html",
                ship_areas=_live_ship_areas(),
                page_title="Thêm hoạt động mới",
            )
        return redirect(url_for("activities.activities"))

    return render_template(
        "activities/new_activity.html",
        ship_areas=_live_ship_areas(),
        page_title="Thêm hoạt động mới",
    )


@activities_bp.route("/<activity_id>/guests")
@login_required
@activity_access
def activity_guests(activity_id):
    activity = get_activity_by_id(activity_id)
    if not activity:
        flash("Không tìm thấy hoạt động.", "danger")
        return redirect(url_for("activities.activities"))
    return render_template("activities/activity_detail.html", activity=activity, page_title="Danh sách khách")


@activities_bp.route("/<activity_id>/edit", methods=["GET", "POST"])
@login_required
@activity_access
def edit_activity(activity_id):
    activity = get_activity_by_id(activity_id) or next((item for item in _live_activities() if item["id"] == activity_id), None)
    if not activity:
        flash("Không tìm thấy hoạt động.", "danger")
        return redirect(url_for("activities.activities"))

    if request.method == "POST":
        payload = _activity_payload(request.form, _cruise_day(activity.get("cruise_day_id")))
        try:
            get_supabase_client().table("activities").update(payload).eq("id", activity_id).execute()
            flash("Đã cập nhật hoạt động trên Supabase.", "success")
        except Exception:
            activity.update(payload)
            flash("Chưa cập nhật được Supabase, thay đổi chỉ có hiệu lực trong phiên hiện tại.", "warning")
        return redirect(url_for("activities.activity_guests", activity_id=activity_id))

    return render_template(
        "activities/edit_activity.html",
        activity=activity,
        ship_areas=_live_ship_areas(),
        page_title="Sửa hoạt động",
    )
