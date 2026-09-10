from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

excursions_bp = Blueprint(
    "excursions",
    __name__,
    url_prefix="/excursions"
)

excursions_data = [
    {
        "id": 1,
        "name": "Tour Phú Quốc - Hòn Thơm",
        "date": "2026-09-12",
        "time": "08:00 - 16:00",
        "location": "Phú Quốc",
        "provider": "Phú Quốc Travel",
        "capacity": 80,
        "registered": 72,
        "price": 1500000,
        "status": "Sắp diễn ra",
        "description": "Khám phá Phú Quốc và Hòn Thơm với nhiều hoạt động tham quan.",
        "rating": 4.8,
        "feedback_count": 35
    },
    {
        "id": 2,
        "name": "Lặn ngắm san hô Cát Bà",
        "date": "2026-09-11",
        "time": "09:00 - 15:00",
        "location": "Cát Bà",
        "provider": "Cat Ba Ocean Tour",
        "capacity": 30,
        "registered": 30,
        "price": 950000,
        "status": "Sắp diễn ra",
        "description": "Trải nghiệm lặn ngắm san hô cùng hướng dẫn viên chuyên nghiệp.",
        "rating": 4.7,
        "feedback_count": 21
    },
    {
        "id": 3,
        "name": "City Tour Nha Trang",
        "date": "2026-08-21",
        "time": "08:30 - 14:00",
        "location": "Nha Trang",
        "provider": "Nha Trang Explorer",
        "capacity": 100,
        "registered": 88,
        "price": 600000,
        "status": "Hoàn thành",
        "description": "Tham quan các địa điểm nổi tiếng tại thành phố Nha Trang.",
        "rating": 4.6,
        "feedback_count": 42
    }
]

providers_data = [
    {
        "id": 1,
        "name": "Phú Quốc Travel",
        "contact_person": "Nguyễn Hoàng Nam",
        "phone": "0901234567",
        "email": "contact@phuquoctravel.vn",
        "address": "Phú Quốc, Kiên Giang",
        "status": "Đang hợp tác",
        "excursion_count": 1
    },
    {
        "id": 2,
        "name": "Cat Ba Ocean Tour",
        "contact_person": "Trần Minh Đức",
        "phone": "0912345678",
        "email": "info@catbaocean.vn",
        "address": "Cát Bà, Hải Phòng",
        "status": "Đang hợp tác",
        "excursion_count": 1
    },
    {
        "id": 3,
        "name": "Nha Trang Explorer",
        "contact_person": "Lê Quốc Anh",
        "phone": "0923456789",
        "email": "hello@nhatrangexplorer.vn",
        "address": "Nha Trang, Khánh Hòa",
        "status": "Đang hợp tác",
        "excursion_count": 1
    }
]

excursion_registrations = {
    1: [
        {
            "id": 1,
            "guest_code": "G004",
            "name": "Phạm Minh Tuấn",
            "room": "B201",
            "registered_at": "09/09/2026",
            "checked_in": True,
            "rating": 5,
            "feedback": "Tour rất thú vị"
        },
        {
            "id": 2,
            "guest_code": "G005",
            "name": "Võ Thị Lan",
            "room": "B202",
            "registered_at": "10/09/2026",
            "checked_in": False,
            "rating": 0,
            "feedback": ""
        }
    ],
    2: [
        {
            "id": 3,
            "guest_code": "G006",
            "name": "Đặng Quốc Huy",
            "room": "B301",
            "registered_at": "09/09/2026",
            "checked_in": False,
            "rating": 0,
            "feedback": ""
        }
    ],
    3: []
}


def excursion_access(f):
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


def excursion_manager_access(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role not in [
            "shore_excursion_manager",
            "admin"
        ]:
            flash("Bạn không có quyền thực hiện thao tác này.", "danger")
            return redirect(url_for("excursions.excursions"))

        return f(*args, **kwargs)

    return decorated_function


@excursions_bp.route("/")
@excursion_access
def excursions():
    return render_template(
        "excursions/excursions.html",
        excursions=excursions_data
    )


@excursions_bp.route("/create", methods=["GET", "POST"])
@excursion_manager_access
def create_excursion():
    if request.method == "POST":
        excursion_id = max(
            [item["id"] for item in excursions_data],
            default=0
        ) + 1

        provider_id = request.form.get("provider_id")

        provider = next(
            (
                item
                for item in providers_data
                if str(item["id"]) == str(provider_id)
            ),
            None
        )

        new_excursion = {
            "id": excursion_id,
            "name": request.form.get("name", ""),
            "date": request.form.get("date", ""),
            "time": request.form.get("time", ""),
            "location": request.form.get("location", ""),
            "provider": provider["name"] if provider else "",
            "capacity": int(request.form.get("capacity", 0)),
            "registered": 0,
            "price": int(request.form.get("price", 0)),
            "status": request.form.get(
                "status",
                "Sắp diễn ra"
            ),
            "description": request.form.get(
                "description",
                ""
            ),
            "rating": 0,
            "feedback_count": 0
        }

        excursions_data.append(new_excursion)

        excursion_registrations[excursion_id] = []

        if provider:
            provider["excursion_count"] += 1

        flash(
            "Tạo tour thành công.",
            "success"
        )

        return redirect(
            url_for("excursions.excursions")
        )

    return render_template(
        "excursions/excursion_form.html",
        providers=providers_data,
        edit_mode=False
    )


@excursions_bp.route("/<int:excursion_id>")
@excursion_access
def excursion_detail(excursion_id):
    excursion = next(
        (
            item
            for item in excursions_data
            if item["id"] == excursion_id
        ),
        None
    )

    if excursion is None:
        flash(
            "Không tìm thấy tour.",
            "danger"
        )

        return redirect(
            url_for("excursions.excursions")
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
    excursion = next(
        (
            item
            for item in excursions_data
            if item["id"] == excursion_id
        ),
        None
    )

    if excursion is None:
        flash(
            "Không tìm thấy tour.",
            "danger"
        )

        return redirect(
            url_for("excursions.excursions")
        )

    old_provider = next(
        (
            item
            for item in providers_data
            if item["name"] == excursion["provider"]
        ),
        None
    )

    if request.method == "POST":
        excursion["name"] = request.form.get(
            "name",
            ""
        )

        excursion["date"] = request.form.get(
            "date",
            ""
        )

        excursion["time"] = request.form.get(
            "time",
            ""
        )

        excursion["location"] = request.form.get(
            "location",
            ""
        )

        excursion["capacity"] = int(
            request.form.get(
                "capacity",
                0
            )
        )

        excursion["price"] = int(
            request.form.get(
                "price",
                0
            )
        )

        excursion["status"] = request.form.get(
            "status",
            "Sắp diễn ra"
        )

        excursion["description"] = request.form.get(
            "description",
            ""
        )

        provider_id = request.form.get(
            "provider_id"
        )

        new_provider = next(
            (
                item
                for item in providers_data
                if str(item["id"]) == str(provider_id)
            ),
            None
        )

        if new_provider:
            if old_provider and old_provider["id"] != new_provider["id"]:
                if old_provider["excursion_count"] > 0:
                    old_provider["excursion_count"] -= 1

                new_provider["excursion_count"] += 1

            excursion["provider"] = new_provider["name"]

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
        excursion=excursion,
        providers=providers_data,
        edit_mode=True
    )


@excursions_bp.route("/providers")
@excursion_manager_access
def providers():
    return render_template(
        "excursions/providers.html",
        providers=providers_data
    )


@excursions_bp.route(
    "/providers/create",
    methods=["POST"]
)
@excursion_manager_access
def create_provider():
    provider_id = max(
        [item["id"] for item in providers_data],
        default=0
    ) + 1

    new_provider = {
        "id": provider_id,
        "name": request.form.get(
            "name",
            ""
        ),
        "contact_person": request.form.get(
            "contact_person",
            ""
        ),
        "phone": request.form.get(
            "phone",
            ""
        ),
        "email": request.form.get(
            "email",
            ""
        ),
        "address": request.form.get(
            "address",
            ""
        ),
        "status": request.form.get(
            "status",
            "Đang hợp tác"
        ),
        "excursion_count": 0
    }

    providers_data.append(
        new_provider
    )

    flash(
        "Thêm nhà cung cấp thành công.",
        "success"
    )

    return redirect(
        url_for("excursions.providers")
    )


@excursions_bp.route(
    "/<int:excursion_id>/registrations"
)
@excursion_access
def excursion_registrations_list(excursion_id):
    excursion = next(
        (
            item
            for item in excursions_data
            if item["id"] == excursion_id
        ),
        None
    )

    if excursion is None:
        flash(
            "Không tìm thấy tour.",
            "danger"
        )

        return redirect(
            url_for("excursions.excursions")
        )

    registrations = excursion_registrations.get(
        excursion_id,
        []
    )

    return render_template(
        "activities/registrations.html",
        activity=excursion,
        registrations=registrations,
        is_excursion=True
    )


@excursions_bp.route(
    "/<int:excursion_id>/registrations/<int:registration_id>/checkin",
    methods=["POST"]
)
@excursion_access
def excursion_checkin(
    excursion_id,
    registration_id
):
    registrations = excursion_registrations.get(
        excursion_id,
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
                "excursions.excursion_registrations_list",
                excursion_id=excursion_id
            )
        )

    registration["checked_in"] = True

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