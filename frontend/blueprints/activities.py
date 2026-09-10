from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

activities_bp = Blueprint("activities", __name__, url_prefix="/activities")

REGISTRATIONS = []
ACTIVITY_CUSTOMERS = {
    1: [
        {"name": "Nguyễn Văn A", "room": "1204", "phone": "0901 111 111", "status": "Paid"},
        {"name": "Trần Thị B", "room": "0812", "phone": "0901 222 222", "status": "Registered"},
    ],
    2: [
        {"name": "Lê Hoàng C", "room": "1501", "phone": "0901 333 333", "status": "Registered"},
    ],
    3: [
        {"name": "Phạm Minh D", "room": "0605", "phone": "0901 444 444", "status": "Registered"},
        {"name": "Võ Thị E", "room": "0606", "phone": "0901 555 555", "status": "Waiting"},
    ],
}

activities_list = [
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

@activities_bp.route("/")
@activities_bp.route("/list")
@login_required
@activity_access
def activities():
    return render_template("activities/activities.html", activities=activities_list, page_title="Quản lý Hoạt động trên tàu")

@activities_bp.route("/customers/<int:activity_id>")
@login_required
@activity_access
def customers(activity_id):
    customers = ACTIVITY_CUSTOMERS.get(activity_id, [])
    activity = next((a for a in activities_list if a["id"] == activity_id), None)
    return render_template("activities/customers.html", customers=customers, activity=activity, page_title="Danh sách khách")

@activities_bp.route("/customers/<int:activity_id>/edit", methods=["GET", "POST"])
@login_required
@activity_access
def edit_customers(activity_id):
    activity = next((a for a in activities_list if a["id"] == activity_id), None)
    if activity is None:
        return render_template("system_admin/403.html"), 404

    if request.method == "POST":
        names = request.form.getlist("name")
        rooms = request.form.getlist("room")
        phones = request.form.getlist("phone")
        statuses = request.form.getlist("status")

        updated = []
        for idx, name in enumerate(names):
            if not name.strip():
                continue
            updated.append({
                "name": name.strip(),
                "room": rooms[idx].strip() if idx < len(rooms) else "",
                "phone": phones[idx].strip() if idx < len(phones) else "",
                "status": statuses[idx].strip() if idx < len(statuses) else "Registered",
            })

        ACTIVITY_CUSTOMERS[activity_id] = updated
        flash("Danh sách khách đã được cập nhật.", "success")
        return redirect(url_for("activities.customers", activity_id=activity_id))

    return render_template("activities/edit_customers.html", activity=activity, customers=ACTIVITY_CUSTOMERS.get(activity_id, []), page_title="Sửa danh sách khách")

@activities_bp.route("/edit/<int:activity_id>", methods=["GET", "POST"])
@login_required
@activity_access
def edit_activity(activity_id):
    activity = next((a for a in activities_list if a["id"] == activity_id), None)
    if activity is None:
        return render_template("system_admin/403.html"), 404

    if request.method == "POST":
        activity["name"] = request.form.get("name", activity["name"])
        activity["location"] = request.form.get("location", activity["location"])
        activity["time"] = request.form.get("time", activity["time"])
        activity["capacity"] = int(request.form.get("capacity", activity["capacity"]) or activity["capacity"])
        activity["price"] = int(request.form.get("price", activity["price"]) or 0)
        activity["type"] = "Miễn phí" if activity["price"] == 0 else "Trả phí"
        flash("Hoạt động đã được cập nhật.", "success")
        return redirect(url_for("activities.activities"))

    return render_template("activities/edit_activity.html", activity=activity, page_title="Sửa hoạt động")

@activities_bp.route("/register", methods=["GET", "POST"])
@login_required
@activity_access
def register_activity():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        time = request.form.get("time", "").strip()
        capacity = int(request.form.get("capacity") or 0)
        price = int(request.form.get("price") or 0)

        if not name or not location or not time or capacity <= 0:
            flash("Vui lòng nhập đầy đủ thông tin hoạt động mới.", "danger")
            return render_template("activities/register_activity.html", title="Tạo hoạt động mới")

        new_id = max([a.get("id", 0) for a in activities_list], default=0) + 1
        new_activity = {
            "id": new_id,
            "name": name,
            "location": location,
            "time": time,
            "capacity": capacity,
            "registered": 0,
            "price": price,
            "type": "Miễn phí" if price == 0 else "Trả phí",
        }
        activities_list.append(new_activity)
        flash("Hoạt động mới đã được tạo.", "success")
        return redirect(url_for("activities.activities"))

    return render_template("activities/register_activity.html", title="Tạo hoạt động mới")
