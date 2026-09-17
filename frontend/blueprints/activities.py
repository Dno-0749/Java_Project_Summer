from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json

from config import Config


activities_bp = Blueprint(
    "activities",
    __name__,
    url_prefix="/activities"
)


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


def api_request(path, method="GET", data=None):
    url = f"{Config.API_BASE_URL}{path}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    body = None

    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")

    req = Request(
        url,
        data=body,
        headers=headers,
        method=method
    )

    try:
        with urlopen(req, timeout=10) as response:
            raw = response.read().decode("utf-8")

            if not raw:
                return {}

            return json.loads(raw)

    except HTTPError as e:
        try:
            raw = e.read().decode("utf-8")
            error_data = json.loads(raw)
        except Exception:
            error_data = {
                "message": str(e)
            }

        return {
            "_error": True,
            "status": e.code,
            "message": error_data
        }

    except URLError as e:
        return {
            "_error": True,
            "status": 0,
            "message": f"Không kết nối được Backend: {e}"
        }

    except Exception as e:
        return {
            "_error": True,
            "status": 0,
            "message": str(e)
        }


def normalize_activity(item):
    return {
        "id": item.get("id"),
        "name": item.get("name", ""),
        "location": item.get("location", ""),
        "date": item.get("date", ""),
        "time": item.get("time", ""),
        "capacity": item.get("capacity", 0),
        "registered": item.get("registered", 0),
        "price": item.get("price", 0),
        "type": item.get(
            "activity_type",
            item.get("type", "Miễn phí")
        ),
        "activity_type": item.get(
            "activity_type",
            item.get("type", "Miễn phí")
        ),
        "status": item.get("status", "Sắp diễn ra"),
        "description": item.get("description", ""),
        "rating": item.get("rating", 0),
        "feedback_count": item.get("feedback_count", 0),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at")
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
            flash(
                "Bạn không có quyền thực hiện thao tác này.",
                "danger"
            )
            return redirect(
                url_for("activities.activities")
            )

        return f(*args, **kwargs)

    return decorated_function


@activities_bp.route("/")
@activity_access
def activities():
    result = api_request(
        "/api/activities/",
        method="GET"
    )

    if result.get("_error"):
        flash(
            "Không lấy được dữ liệu hoạt động từ Backend.",
            "danger"
        )

        return render_template(
            "activities/activities.html",
            activities=[]
        )

    activities_data = [
        normalize_activity(item)
        for item in result
    ]

    return render_template(
        "activities/activities.html",
        activities=activities_data
    )


@activities_bp.route("/create", methods=["GET", "POST"])
@manager_access
def create_activity():
    if request.method == "POST":
        start_time = request.form.get(
            "start_time",
            ""
        )

        end_time = request.form.get(
            "end_time",
            ""
        )

        activity_type = request.form.get(
            "type",
            "Miễn phí"
        )

        payload = {
            "name": request.form.get(
                "name",
                ""
            ).strip(),

            "location": request.form.get(
                "location",
                ""
            ).strip(),

            "description": request.form.get(
                "description",
                ""
            ).strip(),

            "status": request.form.get(
                "status",
                "Sắp diễn ra"
            ),

            "capacity": int(
                request.form.get(
                    "capacity",
                    0
                ) or 0
            ),

            "registered": 0,

            "price": int(
                request.form.get(
                    "price",
                    0
                ) or 0
            ),

            "activity_type": activity_type
        }

        if start_time or end_time:
            payload["description"] = (
                payload["description"]
                + (
                    f"\nThời gian: {start_time} - {end_time}"
                    if start_time or end_time
                    else ""
                )
            )

        result = api_request(
            "/api/activities/",
            method="POST",
            data=payload
        )

        if result.get("_error"):
            flash(
                f"Tạo hoạt động thất bại: {result.get('message')}",
                "danger"
            )

            return render_template(
                "activities/activity_form.html",
                edit_mode=False
            )

        flash(
            "Tạo hoạt động thành công.",
            "success"
        )

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
    result = api_request(
        f"/api/activities/{activity_id}",
        method="GET"
    )

    if result.get("_error"):
        flash(
            "Không tìm thấy hoạt động.",
            "danger"
        )

        return redirect(
            url_for("activities.activities")
        )

    activity = normalize_activity(result)

    return render_template(
        "activities/activity_detail.html",
        activity=activity
    )


@activities_bp.route(
    "/<int:activity_id>/edit",
    methods=["GET", "POST"]
)
@manager_access
def edit_activity(activity_id):
    result = api_request(
        f"/api/activities/{activity_id}",
        method="GET"
    )

    if result.get("_error"):
        flash(
            "Không tìm thấy hoạt động.",
            "danger"
        )

        return redirect(
            url_for("activities.activities")
        )

    activity = normalize_activity(result)

    if request.method == "POST":
        start_time = request.form.get(
            "start_time",
            ""
        )

        end_time = request.form.get(
            "end_time",
            ""
        )

        activity_type = request.form.get(
            "type",
            activity.get(
                "activity_type",
                "Miễn phí"
            )
        )

        description = request.form.get(
            "description",
            ""
        ).strip()

        if start_time or end_time:
            description = (
                description
                + f"\nThời gian: {start_time} - {end_time}"
            )

        payload = {
            "name": request.form.get(
                "name",
                ""
            ).strip(),

            "location": request.form.get(
                "location",
                ""
            ).strip(),

            "description": description,

            "status": request.form.get(
                "status",
                "Sắp diễn ra"
            ),

            "capacity": int(
                request.form.get(
                    "capacity",
                    0
                ) or 0
            ),

            "registered": activity.get(
                "registered",
                0
            ),

            "price": int(
                request.form.get(
                    "price",
                    0
                ) or 0
            ),

            "activity_type": activity_type
        }

        update_result = api_request(
            f"/api/activities/{activity_id}",
            method="PUT",
            data=payload
        )

        if update_result.get("_error"):
            flash(
                f"Cập nhật thất bại: {update_result.get('message')}",
                "danger"
            )

            return render_template(
                "activities/activity_form.html",
                activity=activity,
                edit_mode=True
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
    result = api_request(
        f"/api/activities/{activity_id}",
        method="GET"
    )

    if result.get("_error"):
        flash(
            "Không tìm thấy hoạt động.",
            "danger"
        )

        return redirect(
            url_for("activities.activities")
        )

    activity = normalize_activity(result)

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


@activities_bp.route(
    "/<int:activity_id>/delete",
    methods=["POST"]
)
@manager_access
def delete_activity(activity_id):
    result = api_request(
        f"/api/activities/{activity_id}",
        method="DELETE"
    )

    if result.get("_error"):
        flash(
            f"Xóa hoạt động thất bại: {result.get('message')}",
            "danger"
        )

        return redirect(
            url_for("activities.activities")
        )

    registrations_data.pop(
        activity_id,
        None
    )

    flash(
        "Xóa hoạt động thành công.",
        "success"
    )

    return redirect(
        url_for("activities.activities")
    )