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
    return render_template("coordinator/itinerary.html", bookings=bookings, page_title="Quản lý Lịch trình")


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
