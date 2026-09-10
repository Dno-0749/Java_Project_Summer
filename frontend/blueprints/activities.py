from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

activities_bp = Blueprint(
    "activities",
    __name__,
    url_prefix="/activities"
)

activities_data = [
    {
        "id": 1,
        "name": "Yoga buổi sáng",
        "location": "Sundeck",
        "date": "2026-09-12",
        "time": "06:30 - 07:30",
        "capacity": 40,
        "registered": 35,
        "price": 0,
        "type": "Miễn phí",
        "status": "Đang diễn ra",
        "description": "Buổi tập yoga buổi sáng dành cho hành khách trên tàu.",
        "rating": 4.8,
        "feedback_count": 24
    },
    {
        "id": 2,
        "name": "Wine Tasting",
        "location": "Sky Lounge",
        "date": "2026-09-12",
        "time": "16:00 - 17:30",
        "capacity": 25,
        "registered": 25,
        "price": 850000,
        "type": "Trả phí",
        "status": "Sắp diễn ra",
        "description": "Trải nghiệm thưởng thức và tìm hiểu các loại rượu.",
        "rating": 4.7,
        "feedback_count": 18
    },
    {
        "id": 3,
        "name": "Live Music Night",
        "location": "Main Stage",
        "date": "2026-09-12",
        "time": "20:00 - 22:00",
        "capacity": 200,
        "registered": 178,
        "price": 0,
        "type": "Miễn phí",
        "status": "Sắp diễn ra",
        "description": "Đêm nhạc trực tiếp tại sân khấu chính của tàu.",
        "rating": 4.9,
        "feedback_count": 42
    },
    {
        "id": 4,
        "name": "Cooking Class",
        "location": "Culinary Studio",
        "date": "2026-09-13",
        "time": "10:00 - 12:00",
        "capacity": 15,
        "registered": 12,
        "price": 1200000,
        "type": "Trả phí",
        "status": "Sắp diễn ra",
        "description": "Lớp học nấu ăn cùng đầu bếp chuyên nghiệp.",
        "rating": 4.6,
        "feedback_count": 15
    },
    {
        "id": 5,
        "name": "Kids Club",
        "location": "Kids Zone",
        "date": "2026-09-13",
        "time": "09:00 - 11:00",
        "capacity": 30,
        "registered": 22,
        "price": 0,
        "type": "Miễn phí",
        "status": "Sắp diễn ra",
        "description": "Khu vui chơi và hoạt động dành cho trẻ em.",
        "rating": 4.8,
        "feedback_count": 20
    }
]

registrations_data = {
    1: [
        {
            "id": 1,
            "guest_code": "G001",
            "name": "Nguyễn Văn An",
            "room": "A101",
            "registered_at": "10/09/2026",
            "checked_in": True,
            "rating": 5,
            "feedback": "Rất tuyệt vời"
        },
        {
            "id": 2,
            "guest_code": "G002",
            "name": "Trần Thị Bình",
            "room": "A102",
            "registered_at": "10/09/2026",
            "checked_in": False,
            "rating": 0,
            "feedback": ""
        },
        {
            "id": 3,
            "guest_code": "G003",
            "name": "Lê Minh Anh",
            "room": "A103",
            "registered_at": "11/09/2026",
            "checked_in": True,
            "rating": 5,
            "feedback": "Hoạt động rất thú vị"
        }
    ]
}


def activity_access(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role not in [
            "activity_manager",
            "operations",
            "admin",
            "passenger",
            "shore_excursion_manager"
        ]:
            flash("Bạn không có quyền truy cập.", "danger")
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorated_function


def manager_access(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role not in [
            "activity_manager",
            "admin"
        ]:
            flash("Bạn không có quyền thực hiện thao tác này.", "danger")
            return redirect(url_for("activities.activities"))

        return f(*args, **kwargs)

    return decorated_function


@activities_bp.route("/")
@activity_access
def activities():
    return render_template(
        "activities/activities.html",
        activities=activities_data
    )


@activities_bp.route("/create", methods=["GET", "POST"])
@manager_access
def create_activity():
    if request.method == "POST":
        activity_id = max(
            [activity["id"] for activity in activities_data],
            default=0
        ) + 1

        start_time = request.form.get("start_time", "")
        end_time = request.form.get("end_time", "")

        new_activity = {
            "id": activity_id,
            "name": request.form.get("name", ""),
            "location": request.form.get("location", ""),
            "date": request.form.get("date", ""),
            "time": f"{start_time} - {end_time}",
            "capacity": int(request.form.get("capacity", 0)),
            "registered": 0,
            "price": int(request.form.get("price", 0)),
            "type": request.form.get("type", "Miễn phí"),
            "status": request.form.get("status", "Sắp diễn ra"),
            "description": request.form.get("description", ""),
            "rating": 0,
            "feedback_count": 0
        }

        activities_data.append(new_activity)

        flash("Tạo hoạt động thành công.", "success")

        return redirect(
            url_for("activities.activities")
        )

    return render_template(
        "activities/activity_form.html",
        edit_mode=False
    )


@activities_bp.route("/<int:activity_id>")
@activity_access
def activity_detail(activity_id):
    activity = next(
        (
            item
            for item in activities_data
            if item["id"] == activity_id
        ),
        None
    )

    if activity is None:
        flash("Không tìm thấy hoạt động.", "danger")

        return redirect(
            url_for("activities.activities")
        )

    return render_template(
        "activities/activity_detail.html",
        activity=activity
    )


@activities_bp.route("/<int:activity_id>/edit", methods=["GET", "POST"])
@manager_access
def edit_activity(activity_id):
    activity = next(
        (
            item
            for item in activities_data
            if item["id"] == activity_id
        ),
        None
    )

    if activity is None:
        flash("Không tìm thấy hoạt động.", "danger")

        return redirect(
            url_for("activities.activities")
        )

    if request.method == "POST":
        activity["name"] = request.form.get(
            "name",
            ""
        )

        activity["location"] = request.form.get(
            "location",
            ""
        )

        activity["date"] = request.form.get(
            "date",
            ""
        )

        activity["capacity"] = int(
            request.form.get(
                "capacity",
                0
            )
        )

        activity["price"] = int(
            request.form.get(
                "price",
                0
            )
        )

        activity["type"] = request.form.get(
            "type",
            "Miễn phí"
        )

        activity["status"] = request.form.get(
            "status",
            "Sắp diễn ra"
        )

        activity["description"] = request.form.get(
            "description",
            ""
        )

        start_time = request.form.get(
            "start_time",
            ""
        )

        end_time = request.form.get(
            "end_time",
            ""
        )

        if start_time or end_time:
            activity["time"] = (
                f"{start_time} - {end_time}"
            )

        flash(
            "Cập nhật hoạt động thành công.",
            "success"
        )

        return redirect(
            url_for(
                "activities.activity_detail",
                activity_id=activity_id
            )
        )

    return render_template(
        "activities/activity_form.html",
        activity=activity,
        edit_mode=True
    )


@activities_bp.route("/<int:activity_id>/registrations")
@activity_access
def registrations(activity_id):
    activity = next(
        (
            item
            for item in activities_data
            if item["id"] == activity_id
        ),
        None
    )

    if activity is None:
        flash("Không tìm thấy hoạt động.", "danger")

        return redirect(
            url_for("activities.activities")
        )

    registrations = registrations_data.get(
        activity_id,
        []
    )

    return render_template(
        "activities/registrations.html",
        activity=activity,
        registrations=registrations
    )


@activities_bp.route(
    "/<int:activity_id>/registrations/<int:registration_id>/checkin",
    methods=["POST"]
)
@activity_access
def checkin(activity_id, registration_id):
    registrations = registrations_data.get(
        activity_id,
        []
    )

    registration = next(
        (
            item
            for item in registrations
            if item["id"] == registration_id
        ),
        None
    )

    if registration is None:
        flash(
            "Không tìm thấy đăng ký.",
            "danger"
        )

        return redirect(
            url_for(
                "activities.registrations",
                activity_id=activity_id
            )
        )

    registration["checked_in"] = True

    flash(
        "Check-in thành công.",
        "success"
    )

    return redirect(
        url_for(
            "activities.registrations",
            activity_id=activity_id
        )
    )