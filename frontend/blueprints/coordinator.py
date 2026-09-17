from flask import Blueprint, flash, redirect, render_template, request, url_for
import api_client
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
    bookings, error = api_client.list_bookings()
    if error:
        flash(error, "danger")
        bookings = []
    cruises, cruise_error = api_client.list_cruises()
    ports, port_error = api_client.list_ports()
    if cruise_error:
        flash(cruise_error, "danger")
        cruises = []
    if port_error:
        flash(port_error, "danger")
        ports = []

    selected_cruise_id = request.args.get("cruise_id", type=int)
    if selected_cruise_id is None and cruises:
        selected_cruise_id = cruises[0].get("id")
    cruise_days = []
    if selected_cruise_id:
        cruise_days, day_error = api_client.list_cruise_days(selected_cruise_id)
        if day_error:
            flash(day_error, "danger")
            cruise_days = []
    selected_cruise = next(
        (cruise for cruise in cruises if cruise.get("id") == selected_cruise_id),
        None,
    )
    return render_template(
        "coordinator/itinerary.html",
        bookings=bookings,
        cruises=cruises,
        ports=ports,
        cruise_days=cruise_days,
        selected_cruise_id=selected_cruise_id,
        selected_cruise=selected_cruise,
        page_title="Quản lý Lịch trình",
    )


@coordinator_bp.route("/ports", methods=["POST"])
@login_required
@coordinator_access
def create_port():
    data = {
        "name": request.form.get("name", "").strip(),
        "country": request.form.get("country", "").strip(),
        "description": request.form.get("description", "").strip(),
    }
    _, error = api_client.create_port(data)
    flash(error or "Đã tạo cảng/điểm dừng.", "danger" if error else "success")
    return redirect(url_for("coordinator.itinerary"))


@coordinator_bp.route("/cruise-days/<int:day_id>/update", methods=["POST"])
@login_required
@coordinator_access
def update_cruise_day(day_id):
    cruise_id = request.form.get("cruise_id", type=int)
    data = {
        "day_number": request.form.get("day_number", "").strip(),
        "date": request.form.get("date", "").strip(),
        "port_id": request.form.get("port_id") or None,
        "arrival_time": request.form.get("arrival_time") or None,
        "departure_time": request.form.get("departure_time") or None,
    }
    _, error = api_client.update_cruise_day(day_id, data)
    flash(error or "Đã cập nhật cảng và giờ cập/rời bến.", "danger" if error else "success")
    return redirect(url_for("coordinator.itinerary", cruise_id=cruise_id))


@coordinator_bp.route("/cruises/<int:cruise_id>/days", methods=["POST"])
@login_required
@coordinator_access
def create_cruise_day(cruise_id):
    data = {
        "day_number": request.form.get("day_number", "").strip(),
        "date": request.form.get("date", "").strip(),
        "port_id": request.form.get("port_id") or None,
        "arrival_time": request.form.get("arrival_time") or None,
        "departure_time": request.form.get("departure_time") or None,
    }
    _, error = api_client.create_cruise_day(cruise_id, data)
    flash(error or "Đã thêm cảng và giờ vào lịch trình.", "danger" if error else "success")
    return redirect(url_for("coordinator.itinerary", cruise_id=cruise_id))


@coordinator_bp.route("/bookings", methods=["POST"])
@login_required
@coordinator_access
def create_booking():
    data = {key: request.form.get(key, "").strip() for key in ("ship_name", "customer_name", "start_date", "end_date", "status")}
    data["status"] = data["status"] or "pending"
    _, error = api_client.create_booking(data)
    flash(error or "Đã tạo booking.", "danger" if error else "success")
    return redirect(url_for("coordinator.itinerary"))


@coordinator_bp.route("/bookings/<int:booking_id>/update", methods=["POST"])
@login_required
@coordinator_access
def edit_booking(booking_id):
    data = {key: request.form.get(key, "").strip() for key in ("ship_name", "customer_name", "start_date", "end_date", "status")}
    _, error = api_client.update_booking(booking_id, data)
    flash(error or "Đã cập nhật booking.", "danger" if error else "success")
    return redirect(url_for("coordinator.itinerary"))


@coordinator_bp.route("/bookings/<int:booking_id>/delete", methods=["POST"])
@login_required
@coordinator_access
def delete_booking(booking_id):
    _, error = api_client.delete_booking(booking_id)
    flash(error or "Đã xóa booking.", "danger" if error else "success")
    return redirect(url_for("coordinator.itinerary"))


@coordinator_bp.route("/bookings/<int:booking_id>/status", methods=["POST"])
@login_required
@coordinator_access
def update_booking_status(booking_id):
    _, error = api_client.update_booking_status(booking_id, request.form.get("status", "pending"))
    flash(error or "Đã cập nhật trạng thái.", "danger" if error else "success")
    return redirect(url_for("coordinator.itinerary"))


@coordinator_bp.route("/bookings/statuses", methods=["POST"])
@login_required
@coordinator_access
def update_booking_statuses():
    errors = []
    updated_count = 0

    for field_name, status in request.form.items():
        if not field_name.startswith("status_"):
            continue
        try:
            booking_id = int(field_name.removeprefix("status_"))
        except ValueError:
            errors.append(f"Mã booking không hợp lệ: {field_name}")
            continue

        _, error = api_client.update_booking_status(booking_id, status)
        if error:
            errors.append(f"Booking #{booking_id}: {error}")
        else:
            updated_count += 1

    if errors:
        flash("Đã lưu một phần thay đổi. " + " | ".join(errors), "danger")
    elif updated_count:
        flash(f"Đã lưu trạng thái cho {updated_count} booking.", "success")
    else:
        flash("Không có thay đổi nào để lưu.", "warning")
    return redirect(url_for("coordinator.itinerary"))
