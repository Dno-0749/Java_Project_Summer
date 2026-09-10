from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import wraps

activities_bp = Blueprint("activities", __name__, url_prefix="/activities")

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
    activities_list = [
        {"id": 1, "name": "Yoga buổi sáng", "location": "Sundeck", "time": "06:30 - 07:30", "capacity": 40, "registered": 35, "price": 0, "type": "Miễn phí"},
        {"id": 2, "name": "Wine Tasting", "location": "Sky Lounge", "time": "16:00 - 17:30", "capacity": 25, "registered": 25, "price": 850000, "type": "Trả phí"},
        {"id": 3, "name": "Live Music Night", "location": "Main Stage", "time": "20:00 - 22:00", "capacity": 200, "registered": 178, "price": 0, "type": "Miễn phí"},
        {"id": 4, "name": "Cooking Class", "location": "Culinary Studio", "time": "10:00 - 12:00", "capacity": 15, "registered": 12, "price": 1200000, "type": "Trả phí"},
        {"id": 5, "name": "Kids Club", "location": "Kids Zone", "time": "09:00 - 11:00", "capacity": 30, "registered": 22, "price": 0, "type": "Miễn phí"},
    ]
    return render_template("activities/activities.html", activities=activities_list, page_title="Quản lý Hoạt động trên tàu")
