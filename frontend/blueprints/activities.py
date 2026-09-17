from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
import api_client

activities_bp = Blueprint("activities", __name__, url_prefix="/activities")


def activity_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["activity_manager", "operations", "admin"]:
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function


def _fmt_time(iso_str):
    if not iso_str:
        return "-"
    try:
        from datetime import datetime
        return datetime.fromisoformat(iso_str).strftime("%H:%M")
    except Exception:
        return str(iso_str)[:5]


@activities_bp.route("/")
@activities_bp.route("/list")
@login_required
@activity_access
def activities():
    """UC15/UC16: Quản lý hoạt động trên tàu - dữ liệu thật từ Backend."""
    cruise, err = api_client.ensure_demo_cruise()
    if err:
        flash(f"Lỗi kết nối backend: {err}", "danger")
        return render_template("activities/activities.html", activities=[], page_title="Quản lý Hoạt động trên tàu")

    raw_activities, err2 = api_client.list_activities(cruise["id"])
    if err2:
        flash(f"Lỗi tải danh sách hoạt động: {err2}", "danger")
        raw_activities = []

    view_activities = []
    for a in raw_activities or []:
        regs, _ = api_client.list_activity_registrations(a["id"])
        view_activities.append({
            "id": a["id"],
            "name": a["name"],
            "location": a.get("location") or "-",
            "time": f"{_fmt_time(a.get('start_time'))} - {_fmt_time(a.get('end_time'))}",
            "capacity": a.get("capacity") or 0,
            "registered": len(regs or []),
            "price": float(a.get("fee") or 0),
            "type": "Miễn phí" if not a.get("fee") else "Trả phí",
        })

    return render_template(
        "activities/activities.html",
        activities=view_activities,
        cruise=cruise,
        page_title="Quản lý Hoạt động trên tàu",
    )


@activities_bp.route("/create", methods=["GET", "POST"])
@login_required
@activity_access
def create_activity():
    """UC15: Tạo hoạt động mới + UC17: cấu hình giờ/địa điểm/sức chứa/phí."""
    cruise, err = api_client.ensure_demo_cruise()
    if err:
        flash(f"Lỗi kết nối backend: {err}", "danger")
        return redirect(url_for("activities.activities"))

    if request.method == "POST":
        date_str = request.form.get("date", "").strip()
        start_time = request.form.get("start_time", "").strip()
        end_time = request.form.get("end_time", "").strip()

        payload = {
            "name": request.form.get("name", "").strip(),
            "fee": float(request.form.get("fee") or 0),
            "is_included_in_package": request.form.get("is_included_in_package") == "on",
        }
        description = request.form.get("description", "").strip()
        if description:
            payload["description"] = description
        location = request.form.get("location", "").strip()
        if location:
            payload["location"] = location
        capacity = request.form.get("capacity", "").strip()
        if capacity:
            payload["capacity"] = int(capacity)
        if date_str and start_time:
            payload["start_time"] = f"{date_str}T{start_time}:00"
        if date_str and end_time:
            payload["end_time"] = f"{date_str}T{end_time}:00"

        activity, err2 = api_client.create_activity(cruise["id"], payload)
        if err2:
            flash(f"Tạo hoạt động thất bại: {err2}", "danger")
            return render_template("activities/activity_form.html", edit_mode=False, activity=None, page_title="Tạo hoạt động mới")

        flash(f"Đã tạo hoạt động '{activity['name']}' thành công.", "success")
        return redirect(url_for("activities.activities"))

    return render_template("activities/activity_form.html", edit_mode=False, activity=None, page_title="Tạo hoạt động mới")


@activities_bp.route("/<int:activity_id>/edit", methods=["GET", "POST"])
@login_required
@activity_access
def edit_activity(activity_id):
    """Sửa hoạt động đã tạo."""
    if request.method == "POST":
        date_str = request.form.get("date", "").strip()
        start_time = request.form.get("start_time", "").strip()
        end_time = request.form.get("end_time", "").strip()

        payload = {
            "name": request.form.get("name", "").strip(),
            "fee": float(request.form.get("fee") or 0),
            "is_included_in_package": request.form.get("is_included_in_package") == "on",
        }
        description = request.form.get("description", "").strip()
        if description:
            payload["description"] = description
        location = request.form.get("location", "").strip()
        if location:
            payload["location"] = location
        capacity = request.form.get("capacity", "").strip()
        if capacity:
            payload["capacity"] = int(capacity)
        if date_str and start_time:
            payload["start_time"] = f"{date_str}T{start_time}:00"
        if date_str and end_time:
            payload["end_time"] = f"{date_str}T{end_time}:00"

        activity, err = api_client.update_activity(activity_id, payload)
        if err:
            flash(f"Cập nhật thất bại: {err}", "danger")
        else:
            flash(f"Đã cập nhật hoạt động '{activity['name']}'.", "success")
        return redirect(url_for("activities.activities"))

    activity, err = api_client.get_activity(activity_id)
    if err or not activity:
        flash("Không tìm thấy hoạt động này.", "danger")
        return redirect(url_for("activities.activities"))

    # Tách lại date/start_time/end_time từ ISO datetime để đổ vào form
    view = dict(activity)
    start_raw = activity.get("start_time") or ""
    end_raw = activity.get("end_time") or ""
    view["date"] = start_raw[:10] if start_raw else ""
    view["start_time_only"] = _fmt_time(start_raw)
    view["end_time_only"] = _fmt_time(end_raw)

    return render_template("activities/activity_form.html", edit_mode=True, activity=view, page_title="Sửa hoạt động")


@activities_bp.route("/<int:activity_id>")
@login_required
@activity_access
def activity_detail(activity_id):
    activity, err = api_client.get_activity(activity_id)
    if err or not activity:
        flash("Không tìm thấy hoạt động này.", "danger")
        return redirect(url_for("activities.activities"))
    regs, _ = api_client.list_activity_registrations(activity_id)
    return render_template("activities/activity_detail.html", activity=activity, registrations=regs or [], page_title=activity["name"])


@activities_bp.route("/<int:activity_id>/registrations")
@login_required
@activity_access
def registrations(activity_id):
    """UC16/UC20: Quản lý danh sách đăng ký + giám sát tỷ lệ tham gia."""
    activity, err = api_client.get_activity(activity_id)
    if err or not activity:
        flash("Không tìm thấy hoạt động này.", "danger")
        return redirect(url_for("activities.activities"))

    regs, err2 = api_client.list_activity_registrations(activity_id)
    if err2:
        flash(f"Lỗi tải danh sách đăng ký: {err2}", "danger")
        regs = []

    view_regs = [{
        "id": r["id"], "passenger_id": r["passenger_id"],
        "status": r["status"], "registered_at": (r.get("registered_at") or "")[:16],
    } for r in (regs or [])]

    checked_in = sum(1 for r in view_regs if r["status"] == "checked_in")
    return render_template(
        "activities/registrations.html",
        activity=activity, registrations=view_regs,
        checked_in_count=checked_in, total_count=len(view_regs),
        page_title=f"Đăng ký - {activity['name']}",
    )


@activities_bp.route("/<int:activity_id>/delete", methods=["POST"])
@login_required
@activity_access
def delete_activity(activity_id):
    result, err = api_client.delete_activity(activity_id)
    if err:
        flash(f"Không thể xóa hoạt động: {err}", "danger")
    else:
        flash("Đã xóa hoạt động.", "info")
    return redirect(url_for("activities.activities"))
