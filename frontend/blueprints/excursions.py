from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
import api_client

excursions_bp = Blueprint("excursions", __name__, url_prefix="/excursions")


def excursion_access(f):
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


def _get_or_create_day(cruise_id, date_str):
    """Tìm CruiseDay theo đúng ngày (date_str dạng YYYY-MM-DD); nếu chưa
    có ngày nào trong lịch trình khớp, tự tạo mới 1 ngày."""
    days, err = api_client.list_cruise_days(cruise_id)
    if err:
        return None, err
    for d in days or []:
        if d.get("date") == date_str:
            return d, None
    day_number = max((d.get("day_number", 0) for d in (days or [])), default=0) + 1
    return api_client.create_cruise_day(cruise_id, {"day_number": day_number, "date": date_str})


@excursions_bp.route("/")
@login_required
@excursion_access
def excursions():
    """UC21/UC23: Quản lý tham quan bờ - dữ liệu thật từ Backend."""
    cruise, err = api_client.ensure_demo_cruise()
    if err:
        flash(f"Lỗi kết nối backend: {err}", "danger")
        return render_template("excursions/excursions.html", excursions=[], page_title="Tham quan bờ")

    days, err2 = api_client.list_cruise_days(cruise["id"])
    if err2:
        days = []

    view_excursions = []
    for d in days or []:
        raw, err3 = api_client.list_excursions(d["id"])
        if err3:
            continue
        for e in raw or []:
            regs, _ = api_client.list_excursion_registrations(e["id"])
            capacity = e.get("capacity") or 0
            registered = len(regs or [])
            if e["status"] == "cancelled":
                status_label = "Đã hủy"
            elif e["status"] == "completed":
                status_label = "Đã kết thúc"
            elif capacity and registered >= capacity:
                status_label = "Hết chỗ"
            else:
                status_label = "Còn chỗ"
            view_excursions.append({
                "id": e["id"], "name": e["name"], "date": d.get("date"),
                "capacity": capacity, "registered": registered,
                "price": float(e.get("price") or 0), "status": status_label,
                "raw_status": e["status"],
            })

    return render_template("excursions/excursions.html", excursions=view_excursions, cruise=cruise, page_title="Tham quan bờ")


@excursions_bp.route("/create", methods=["GET", "POST"])
@login_required
@excursion_access
def create_excursion():
    """UC21: Tạo tour trên bờ + UC23: giờ tập trung/quay lại/sức chứa/giá."""
    cruise, err = api_client.ensure_demo_cruise()
    if err:
        flash(f"Lỗi kết nối backend: {err}", "danger")
        return redirect(url_for("excursions.excursions"))

    if request.method == "POST":
        date_str = request.form.get("date", "").strip()
        gathering_time = request.form.get("gathering_time", "").strip()
        return_time = request.form.get("return_time", "").strip()

        if not date_str:
            flash("Vui lòng chọn ngày diễn ra tour.", "danger")
            return render_template("excursions/excursion_form.html", edit_mode=False, excursion=None, page_title="Tạo tour trên bờ mới")

        day, err_day = _get_or_create_day(cruise["id"], date_str)
        if err_day or not day:
            flash(f"Không thể xác định ngày lịch trình: {err_day}", "danger")
            return render_template("excursions/excursion_form.html", edit_mode=False, excursion=None, page_title="Tạo tour trên bờ mới")

        payload = {
            "name": request.form.get("name", "").strip(),
            "price": float(request.form.get("price") or 0),
        }
        provider_name = request.form.get("provider_name", "").strip()
        if provider_name:
            payload["provider_name"] = provider_name
        capacity = request.form.get("capacity", "").strip()
        if capacity:
            payload["capacity"] = int(capacity)
        if gathering_time:
            payload["gathering_time"] = f"{date_str}T{gathering_time}:00"
        if return_time:
            payload["return_time"] = f"{date_str}T{return_time}:00"

        excursion, err2 = api_client.create_excursion(day["id"], payload)
        if err2:
            flash(f"Tạo tour thất bại: {err2}", "danger")
            return render_template("excursions/excursion_form.html", edit_mode=False, excursion=None, page_title="Tạo tour trên bờ mới")

        flash(f"Đã tạo tour '{excursion['name']}' thành công.", "success")
        return redirect(url_for("excursions.excursions"))

    return render_template("excursions/excursion_form.html", edit_mode=False, excursion=None, page_title="Tạo tour trên bờ mới")


@excursions_bp.route("/<int:excursion_id>/edit", methods=["GET", "POST"])
@login_required
@excursion_access
def edit_excursion(excursion_id):
    if request.method == "POST":
        date_str = request.form.get("date", "").strip()
        gathering_time = request.form.get("gathering_time", "").strip()
        return_time = request.form.get("return_time", "").strip()

        payload = {
            "name": request.form.get("name", "").strip(),
            "price": float(request.form.get("price") or 0),
        }
        provider_name = request.form.get("provider_name", "").strip()
        if provider_name:
            payload["provider_name"] = provider_name
        capacity = request.form.get("capacity", "").strip()
        if capacity:
            payload["capacity"] = int(capacity)
        if date_str and gathering_time:
            payload["gathering_time"] = f"{date_str}T{gathering_time}:00"
        if date_str and return_time:
            payload["return_time"] = f"{date_str}T{return_time}:00"

        excursion, err = api_client.update_excursion(excursion_id, payload)
        if err:
            flash(f"Cập nhật thất bại: {err}", "danger")
        else:
            flash(f"Đã cập nhật tour '{excursion['name']}'.", "success")
        return redirect(url_for("excursions.excursions"))

    excursion, err = api_client.get_excursion(excursion_id)
    if err or not excursion:
        flash("Không tìm thấy tour này.", "danger")
        return redirect(url_for("excursions.excursions"))

    view = dict(excursion)
    gathering_raw = excursion.get("gathering_time") or ""
    return_raw = excursion.get("return_time") or ""
    view["date"] = gathering_raw[:10] if gathering_raw else ""
    view["gathering_time_only"] = _fmt_time(gathering_raw)
    view["return_time_only"] = _fmt_time(return_raw)

    return render_template("excursions/excursion_form.html", edit_mode=True, excursion=view, page_title="Sửa tour trên bờ")


@excursions_bp.route("/<int:excursion_id>/status", methods=["POST"])
@login_required
@excursion_access
def update_status(excursion_id):
    """UC26: Theo dõi trạng thái tour hoàn thành/hủy/trì hoãn."""
    new_status = request.form.get("status")
    result, err = api_client.update_excursion_status(excursion_id, new_status)
    if err:
        flash(f"Không thể cập nhật trạng thái: {err}", "danger")
    else:
        flash("Đã cập nhật trạng thái tour.", "success")
    return redirect(url_for("excursions.excursions"))


@excursions_bp.route("/<int:excursion_id>/registrations")
@login_required
@excursion_access
def registrations(excursion_id):
    """UC25: Quản lý danh sách hành khách đăng ký tour."""
    excursion, err = api_client.get_excursion(excursion_id)
    if err or not excursion:
        flash("Không tìm thấy tour này.", "danger")
        return redirect(url_for("excursions.excursions"))

    regs, err2 = api_client.list_excursion_registrations(excursion_id)
    if err2:
        flash(f"Lỗi tải danh sách đăng ký: {err2}", "danger")
        regs = []

    view_regs = [{
        "id": r["id"], "passenger_id": r["passenger_id"],
        "status": r["status"], "registered_at": (r.get("registered_at") or "")[:16],
    } for r in (regs or [])]

    return render_template(
        "excursions/registrations.html",
        excursion=excursion, registrations=view_regs,
        page_title=f"Đăng ký - {excursion['name']}",
    )


@excursions_bp.route("/<int:excursion_id>/delete", methods=["POST"])
@login_required
@excursion_access
def delete_excursion(excursion_id):
    result, err = api_client.delete_excursion(excursion_id)
    if err:
        flash(f"Không thể xóa tour: {err}", "danger")
    else:
        flash("Đã xóa tour.", "info")
    return redirect(url_for("excursions.excursions"))
