from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json

from config import Config


excursions_bp = Blueprint(
    "excursions",
    __name__,
    url_prefix="/excursions"
)


STATUS_TO_API = {
    "Sắp diễn ra": "OPEN",
    "Đang diễn ra": "IN_PROGRESS",
    "Hoàn thành": "COMPLETED",
    "Trì hoãn": "DELAYED",
    "Hủy": "CANCELLED"
}


STATUS_FROM_API = {
    "OPEN": "Sắp diễn ra",
    "IN_PROGRESS": "Đang diễn ra",
    "COMPLETED": "Hoàn thành",
    "DELAYED": "Trì hoãn",
    "CANCELLED": "Hủy"
}


def api_request(path, method="GET", data=None):
    url = f"{Config.API_BASE_URL}{path}"

    headers = {
        "Content-Type": "application/json"
    }

    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")

    req = Request(
        url,
        data=body,
        headers=headers,
        method=method
    )

    try:
        with urlopen(req, timeout=10) as response:
            content = response.read().decode("utf-8")

            if not content:
                return {}

            return json.loads(content)

    except HTTPError as e:
        try:
            content = e.read().decode("utf-8")

            return {
                "_error": True,
                "_status": e.code,
                "_data": json.loads(content)
            }

        except Exception:
            return {
                "_error": True,
                "_status": e.code,
                "_data": {}
            }

    except URLError:
        return {
            "_error": True,
            "_status": 0,
            "_data": {
                "message": "Không thể kết nối Backend API."
            }
        }

    except Exception as e:
        return {
            "_error": True,
            "_status": 0,
            "_data": {
                "message": str(e)
            }
        }


def excursion_access(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        role = getattr(
            current_user,
            "role",
            None
        )

        allowed_roles = {
            "activity_manager",
            "operations",
            "admin",
            "passenger",
            "shore_excursion_manager"
        }

        if role not in allowed_roles:
            flash(
                "Bạn không có quyền truy cập chức năng này.",
                "error"
            )

            return redirect(
                url_for("dashboard")
            )

        return f(*args, **kwargs)

    return decorated_function


def excursion_manager_access(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        role = getattr(
            current_user,
            "role",
            None
        )

        allowed_roles = {
            "activity_manager",
            "shore_excursion_manager",
            "operations",
            "admin"
        }

        if role not in allowed_roles:
            flash(
                "Bạn không có quyền quản lý hoạt động trên bờ.",
                "error"
            )

            return redirect(
                url_for("excursions.excursions")
            )

        return f(*args, **kwargs)

    return decorated_function


def normalize_provider(provider):
    item = dict(provider)

    item["phone"] = item.get(
        "phone",
        item.get("contact_phone", "")
    )

    item["email"] = item.get(
        "email",
        item.get("contact_email", "")
    )

    item["contact_person"] = item.get(
        "contact_person",
        ""
    )

    return item


def normalize_excursion(
    excursion,
    providers=None
):
    item = dict(excursion)

    item["status"] = STATUS_FROM_API.get(
        item.get("status"),
        item.get("status", "Sắp diễn ra")
    )

    item["price"] = item.get(
        "price",
        item.get("fee", 0)
    )

    item["registered"] = item.get(
        "registered",
        0
    )

    item["rating"] = item.get(
        "rating",
        0
    )

    item["feedback_count"] = item.get(
        "feedback_count",
        0
    )

    item["provider"] = item.get(
        "provider_name",
        ""
    )

    provider_id = item.get("provider_id")

    if providers:
        for provider in providers:
            if provider.get("id") == provider_id:
                item["provider"] = provider.get(
                    "name",
                    ""
                )
                break

    return item


def get_providers():
    result = api_request(
        "/tour-providers/"
    )

    if result.get("_error"):
        return []

    if not isinstance(result, list):
        return []

    return [
        normalize_provider(item)
        for item in result
    ]


@excursions_bp.route("/")
@excursion_access
def excursions():
    providers = get_providers()

    result = api_request(
        "/shore-excursions/"
    )

    excursions_data = []

    if result.get("_error"):
        flash(
            result.get(
                "_data",
                {}
            ).get(
                "message",
                "Không thể tải danh sách tour."
            ),
            "error"
        )

    elif isinstance(result, list):
        excursions_data = [
            normalize_excursion(
                item,
                providers
            )
            for item in result
        ]

    return render_template(
        "excursions/excursions.html",
        excursions=excursions_data,
        providers=providers
    )


@excursions_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@excursion_manager_access
def create_excursion():
    providers = get_providers()

    if request.method == "POST":
        try:
            provider_id = int(
                request.form.get(
                    "provider_id"
                )
            )

            capacity = int(
                request.form.get(
                    "capacity",
                    0
                )
            )

            price = float(
                request.form.get(
                    "price",
                    0
                )
            )

        except (ValueError, TypeError):
            flash(
                "Dữ liệu số không hợp lệ.",
                "error"
            )

            return render_template(
                "excursions/excursion_form.html",
                providers=providers,
                excursion=None,
                edit_mode=False
            )

        name = request.form.get(
            "name",
            ""
        ).strip()

        date = request.form.get(
            "date",
            ""
        )

        time = request.form.get(
            "time",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Sắp diễn ra"
        )

        description = request.form.get(
            "description",
            ""
        ).strip()

        if not name:
            flash(
                "Vui lòng nhập tên tour.",
                "error"
            )

            return render_template(
                "excursions/excursion_form.html",
                providers=providers,
                excursion=None,
                edit_mode=False
            )

        if capacity <= 0:
            flash(
                "Sức chứa phải lớn hơn 0.",
                "error"
            )

            return render_template(
                "excursions/excursion_form.html",
                providers=providers,
                excursion=None,
                edit_mode=False
            )

        if price < 0:
            flash(
                "Giá tour không được âm.",
                "error"
            )

            return render_template(
                "excursions/excursion_form.html",
                providers=providers,
                excursion=None,
                edit_mode=False
            )

        payload = {
            "provider_id": provider_id,
            "name": name,
            "date": date,
            "time": time,
            "location": location,
            "port_name": location,
            "description": description,
            "duration_hours": 0,
            "capacity": capacity,
            "registered": 0,
            "fee": price,
            "price": price,
            "status": STATUS_TO_API.get(
                status,
                "OPEN"
            )
        }

        result = api_request(
            "/shore-excursions/",
            method="POST",
            data=payload
        )

        if result.get("_error"):
            flash(
                result.get(
                    "_data",
                    {}
                ).get(
                    "message",
                    "Không thể tạo tour."
                ),
                "error"
            )

            return render_template(
                "excursions/excursion_form.html",
                providers=providers,
                excursion=payload,
                edit_mode=False
            )

        flash(
            "Tạo tour thành công.",
            "success"
        )

        return redirect(
            url_for(
                "excursions.excursions"
            )
        )

    return render_template(
        "excursions/excursion_form.html",
        providers=providers,
        excursion=None,
        edit_mode=False
    )


@excursions_bp.route(
    "/<int:excursion_id>"
)
@excursion_access
def excursion_detail(excursion_id):
    providers = get_providers()

    result = api_request(
        f"/shore-excursions/{excursion_id}"
    )

    if result.get("_error"):
        flash(
            "Không tìm thấy tour.",
            "error"
        )

        return redirect(
            url_for(
                "excursions.excursions"
            )
        )

    excursion = normalize_excursion(
        result,
        providers
    )

    return render_template(
        "excursions/excursion_detail.html",
        excursion=excursion
    )


@excursions_bp.route(
    "/<int:excursion_id>/edit",
    methods=["GET", "POST"]
)
@excursion_manager_access
def edit_excursion(excursion_id):
    providers = get_providers()

    result = api_request(
        f"/shore-excursions/{excursion_id}"
    )

    if result.get("_error"):
        flash(
            "Không tìm thấy tour.",
            "error"
        )

        return redirect(
            url_for(
                "excursions.excursions"
            )
        )

    excursion = normalize_excursion(
        result,
        providers
    )

    if request.method == "POST":
        try:
            provider_id = int(
                request.form.get(
                    "provider_id"
                )
            )

            capacity = int(
                request.form.get(
                    "capacity",
                    0
                )
            )

            price = float(
                request.form.get(
                    "price",
                    0
                )
            )

        except (ValueError, TypeError):
            flash(
                "Dữ liệu không hợp lệ.",
                "error"
            )

            return render_template(
                "excursions/excursion_form.html",
                providers=providers,
                excursion=excursion,
                edit_mode=True
            )

        registered = excursion.get(
            "registered",
            0
        )

        if capacity < registered:
            flash(
                "Sức chứa không được nhỏ hơn số người đã đăng ký.",
                "error"
            )

            return render_template(
                "excursions/excursion_form.html",
                providers=providers,
                excursion=excursion,
                edit_mode=True
            )

        payload = {
            "provider_id": provider_id,
            "name": request.form.get(
                "name",
                ""
            ).strip(),
            "date": request.form.get(
                "date",
                ""
            ),
            "time": request.form.get(
                "time",
                ""
            ).strip(),
            "location": request.form.get(
                "location",
                ""
            ).strip(),
            "port_name": request.form.get(
                "location",
                ""
            ).strip(),
            "description": request.form.get(
                "description",
                ""
            ).strip(),
            "capacity": capacity,
            "registered": registered,
            "fee": price,
            "price": price
        }

        update_result = api_request(
            f"/shore-excursions/{excursion_id}",
            method="PUT",
            data=payload
        )

        if update_result.get("_error"):
            flash(
                update_result.get(
                    "_data",
                    {}
                ).get(
                    "message",
                    "Không thể cập nhật tour."
                ),
                "error"
            )

            return render_template(
                "excursions/excursion_form.html",
                providers=providers,
                excursion=excursion,
                edit_mode=True
            )

        status = request.form.get(
            "status",
            "Sắp diễn ra"
        )

        status_result = api_request(
            f"/shore-excursions/{excursion_id}/status",
            method="PUT",
            data={
                "status": STATUS_TO_API.get(
                    status,
                    "OPEN"
                )
            }
        )

        if status_result.get("_error"):
            flash(
                "Thông tin tour đã cập nhật nhưng trạng thái chưa cập nhật được.",
                "warning"
            )
        else:
            flash(
                "Cập nhật tour thành công.",
                "success"
            )

        return redirect(
            url_for(
                "excursions.excursion_detail",
                excursion_id=excursion_id
            )
        )

    return render_template(
        "excursions/excursion_form.html",
        providers=providers,
        excursion=excursion,
        edit_mode=True
    )


@excursions_bp.route("/providers")
@excursion_manager_access
def providers():
    return render_template(
        "excursions/providers.html",
        providers=get_providers()
    )


@excursions_bp.route(
    "/providers/create",
    methods=["POST"]
)
@excursion_manager_access
def create_provider():
    name = request.form.get(
        "name",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    address = request.form.get(
        "address",
        ""
    ).strip()

    if not name:
        flash(
            "Vui lòng nhập tên nhà cung cấp.",
            "error"
        )

        return redirect(
            url_for(
                "excursions.providers"
            )
        )

    result = api_request(
        "/tour-providers/",
        method="POST",
        data={
            "name": name,
            "contact_phone": phone,
            "contact_email": email,
            "address": address
        }
    )

    if result.get("_error"):
        flash(
            result.get(
                "_data",
                {}
            ).get(
                "message",
                "Không thể thêm nhà cung cấp."
            ),
            "error"
        )
    else:
        flash(
            "Thêm nhà cung cấp thành công.",
            "success"
        )

    return redirect(
        url_for(
            "excursions.providers"
        )
    )


@excursions_bp.route(
    "/<int:excursion_id>/registrations"
)
@excursion_access
def excursion_registrations_list(
    excursion_id
):
    providers = get_providers()

    excursion_result = api_request(
        f"/shore-excursions/{excursion_id}"
    )

    if excursion_result.get("_error"):
        flash(
            "Không tìm thấy tour.",
            "error"
        )

        return redirect(
            url_for(
                "excursions.excursions"
            )
        )

    excursion = normalize_excursion(
        excursion_result,
        providers
    )

    result = api_request(
        f"/excursion-registrations/?excursion_id={excursion_id}"
    )

    registrations = []

    if not result.get("_error"):

        if isinstance(result, list):
            registrations = result

        elif isinstance(result, dict):
            registrations = result.get(
                "items",
                result.get("data", [])
            )

    return render_template(
        "excursions/excursion_registrations.html",
        excursion=excursion,
        registrations=registrations
    )


@excursions_bp.route(
    "/<int:excursion_id>/register",
    methods=["POST"]
)
@excursion_access
def register_excursion(excursion_id):
    guest_code = request.form.get(
        "guest_code",
        ""
    ).strip()

    passenger_name = request.form.get(
        "passenger_name",
        ""
    ).strip()

    room = request.form.get(
        "room",
        ""
    ).strip()

    notes = request.form.get(
        "notes",
        ""
    ).strip()

    if not guest_code or not passenger_name:
        flash(
            "Vui lòng nhập mã khách và tên hành khách.",
            "error"
        )

        return redirect(
            url_for(
                "excursions.excursion_detail",
                excursion_id=excursion_id
            )
        )

    result = api_request(
        "/excursion-registrations/",
        method="POST",
        data={
            "excursion_id": excursion_id,
            "guest_code": guest_code,
            "passenger_name": passenger_name,
            "room": room,
            "notes": notes,
            "status": "REGISTERED"
        }
    )

    if result.get("_error"):
        flash(
            result.get(
                "_data",
                {}
            ).get(
                "message",
                "Không thể đăng ký tour."
            ),
            "error"
        )
    else:
        flash(
            "Đăng ký tour thành công.",
            "success"
        )

    return redirect(
        url_for(
            "excursions.excursion_detail",
            excursion_id=excursion_id
        )
    )


@excursions_bp.route(
    "/<int:excursion_id>/registrations/<int:registration_id>/checkin",
    methods=["POST"]
)
@excursion_manager_access
def excursion_checkin(
    excursion_id,
    registration_id
):
    result = api_request(
        f"/excursion-registrations/{registration_id}/checkin",
        method="PUT"
    )

    if result.get("_error"):
        flash(
            result.get(
                "_data",
                {}
            ).get(
                "message",
                "Không thể check-in."
            ),
            "error"
        )
    else:
        flash(
            "Check-in thành công.",
            "success"
        )

    return redirect(
        url_for(
            "excursions.excursion_registrations_list",
            excursion_id=excursion_id
        )
    )