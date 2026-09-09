from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
import store

passenger_bp = Blueprint("passenger", __name__, url_prefix="/passenger")


def passenger_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["passenger", "admin"]:
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function


def _current_passenger():
    """Demo: tài khoản 'passenger' luôn map với hành khách mock đầu tiên."""
    return store.PASSENGERS[0]


@passenger_bp.route("/")
@passenger_bp.route("/home")
@login_required
@passenger_access
def home():
    passenger = _current_passenger()
    today_activities = [a for a in store.PASSENGER_ACTIVITIES if a["day"] == 2][:3]
    unread_count = len(store.NOTIFICATIONS)
    return render_template(
        "passenger/home.html",
        passenger=passenger,
        today_activities=today_activities,
        unread_count=unread_count,
        page_title="Trang chủ",
    )


@passenger_bp.route("/itinerary")
@login_required
@passenger_access
def itinerary():
    return render_template(
        "passenger/itinerary.html",
        itinerary=store.ITINERARY,
        page_title="Lịch trình chuyến đi",
    )


@passenger_bp.route("/activities")
@login_required
@passenger_access
def activities():
    filter_type = request.args.get("filter", "all")
    items = store.PASSENGER_ACTIVITIES
    if filter_type == "free":
        items = [a for a in items if a["price"] == 0]
    elif filter_type == "paid":
        items = [a for a in items if a["price"] > 0]
    return render_template(
        "passenger/activities.html",
        activities=items,
        filter_type=filter_type,
        registrations=store.PASSENGER_REGISTRATIONS,
        page_title="Hoạt động & Tham quan bờ",
    )


@passenger_bp.route("/activities/<int:activity_id>")
@login_required
@passenger_access
def activity_detail(activity_id):
    activity = store.get_activity_by_id(activity_id)
    if not activity:
        flash("Không tìm thấy hoạt động này.", "danger")
        return redirect(url_for("passenger.activities"))
    is_registered = activity_id in store.PASSENGER_REGISTRATIONS
    is_full = activity["registered"] >= activity["capacity"]
    return render_template(
        "passenger/activity_detail.html",
        activity=activity,
        is_registered=is_registered,
        is_full=is_full,
        page_title=activity["name"],
    )


@passenger_bp.route("/activities/<int:activity_id>/register", methods=["POST"])
@login_required
@passenger_access
def register_activity(activity_id):
    activity = store.get_activity_by_id(activity_id)
    if not activity:
        return redirect(url_for("passenger.activities"))

    # Business Rule BR-02: không cho đăng ký vượt quá sức chứa
    if activity["registered"] >= activity["capacity"]:
        flash("Đăng ký thất bại. Hoạt động đã đạt sức chứa tối đa.", "danger")
        return redirect(url_for("passenger.activity_detail", activity_id=activity_id))

    if activity_id not in store.PASSENGER_REGISTRATIONS:
        activity["registered"] += 1
        store.PASSENGER_REGISTRATIONS.add(activity_id)
        flash("Đăng ký hoạt động thành công.", "success")
    return redirect(url_for("passenger.activity_detail", activity_id=activity_id))


@passenger_bp.route("/checkin")
@login_required
@passenger_access
def checkin():
    passenger = _current_passenger()
    return render_template(
        "passenger/checkin.html",
        passenger=passenger,
        page_title="Mã QR check-in",
    )


@passenger_bp.route("/bill")
@login_required
@passenger_access
def bill():
    passenger = _current_passenger()
    my_transactions = [t for t in store.TRANSACTIONS if t["passenger_id"] == passenger["id"]]
    total_spent = sum(t["amount"] for t in my_transactions)
    return render_template(
        "passenger/bill.html",
        passenger=passenger,
        transactions=my_transactions,
        total_spent=total_spent,
        page_title="Chi phí phát sinh",
    )


@passenger_bp.route("/notifications")
@login_required
@passenger_access
def notifications():
    return render_template(
        "passenger/notifications.html",
        notifications=store.NOTIFICATIONS,
        page_title="Thông báo",
    )
