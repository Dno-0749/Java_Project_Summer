from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user
from functools import wraps
from datetime import datetime
import uuid
import api_client
import models
import store

passenger_bp = Blueprint("passenger", __name__, url_prefix="/passenger")


def passenger_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["passenger", "admin"]:
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function


def _fmt_time(iso_str):
    """Chuyển '2026-10-01T06:30:00' -> '06:30'. Trả '-' nếu rỗng/lỗi."""
    if not iso_str:
        return "-"
    try:
        return datetime.fromisoformat(iso_str).strftime("%H:%M")
    except Exception:
        return str(iso_str)[:5]


def _current_cruise_and_passenger():
    """Lấy đúng hành khách THẬT gắn với tài khoản đang đăng nhập
    (current_user.passenger_id). Nếu tài khoản chưa có passenger_id (trường
    hợp tài khoản demo cũ tạo trước khi có tính năng đăng ký riêng), tự tạo
    1 passenger mới trên backend và gán/lưu lại vào tài khoản để lần sau
    dùng luôn, không tạo trùng."""
    cruise, err = api_client.ensure_demo_cruise()
    if err:
        flash(f"Lỗi kết nối backend: {err}", "danger")
        return None, None

    if current_user.passenger_id:
        passenger, err = api_client.get_passenger(current_user.passenger_id)
        if not err and passenger:
            return cruise, passenger
        # passenger_id cũ không còn tồn tại trên backend (VD: đổi database) -> tạo lại

    passenger, err = api_client.create_passenger(cruise["id"], current_user.full_name)
    if err:
        flash(f"Lỗi kết nối backend: {err}", "danger")
        return cruise, None
    models.set_passenger_id(current_user.id, passenger["id"])
    return cruise, passenger


def _passenger_view_model(passenger):
    """Map dữ liệu Passenger + OnboardAccount thật từ backend sang đúng field
    mà template đang dùng (name/cabin/card_id/balance)."""
    account, err = api_client.get_account(passenger["id"])
    balance = float(account["balance"]) if account and not err else 0
    return {
        "id": passenger["id"],
        "name": passenger["full_name"],
        "cabin": passenger.get("cabin_id") or "Chưa xếp phòng",
        "card_id": passenger.get("qr_code") or "-",
        "balance": balance,
    }


@passenger_bp.route("/")
@passenger_bp.route("/home")
@login_required
@passenger_access
def home():
    cruise, passenger = _current_cruise_and_passenger()
    if not passenger:
        return render_template("passenger/home.html", passenger={"name": "-", "cabin": "-", "card_id": "-", "balance": 0},
                                today_activities=[], unread_count=0, page_title="Trang chủ")

    p = _passenger_view_model(passenger)

    activities, err = api_client.list_activities(cruise["id"])
    today_activities = []
    if not err:
        for a in (activities or [])[:3]:
            today_activities.append({
                "id": a["id"],
                "kind": "activity",
                "name": a["name"],
                "location": a.get("location") or "-",
                "time": f"{_fmt_time(a.get('start_time'))} - {_fmt_time(a.get('end_time'))}",
            })

    return render_template(
        "passenger/home.html",
        passenger=p,
        today_activities=today_activities,
        unread_count=4,  # demo tĩnh - hệ thống Notification chưa có API riêng
        page_title="Trang chủ",
    )


@passenger_bp.route("/itinerary")
@login_required
@passenger_access
def itinerary():
    cruise, passenger = _current_cruise_and_passenger()
    if not cruise:
        return render_template("passenger/itinerary.html", itinerary=[], page_title="Lịch trình chuyến đi")

    days, err = api_client.list_cruise_days(cruise["id"])
    ports, _ = api_client.list_ports()
    port_map = {p["id"]: p["name"] for p in (ports or [])}

    itinerary_view = []
    if not err:
        for d in days or []:
            itinerary_view.append({
                "day": d["day_number"],
                "date": d["date"],
                "port": port_map.get(d.get("port_id"), "Trên biển (Sea Day)"),
                "arrival": _fmt_time(d.get("arrival_time")) if d.get("arrival_time") else "-",
                "departure": _fmt_time(d.get("departure_time")) if d.get("departure_time") else "-",
                "notes": "",
            })
    return render_template("passenger/itinerary.html", itinerary=itinerary_view, page_title="Lịch trình chuyến đi")


def _load_all_activities_and_excursions(cruise):
    """Gộp Activity (trên tàu) + ShoreExcursion (trên bờ, theo từng cruise_day)
    thành 1 danh sách thống nhất khớp với template activities.html."""
    result = []

    activities, err = api_client.list_activities(cruise["id"])
    if not err:
        for a in activities or []:
            regs, _ = api_client.list_activity_registrations(a["id"])
            result.append({
                "id": a["id"], "kind": "activity", "type": "activity",
                "name": a["name"], "location": a.get("location") or "-",
                "time": f"{_fmt_time(a.get('start_time'))} - {_fmt_time(a.get('end_time'))}",
                "capacity": a.get("capacity") or 0,
                "registered": len(regs or []),
                "price": float(a.get("fee") or 0),
            })

    days, err = api_client.list_cruise_days(cruise["id"])
    if not err:
        for d in days or []:
            excursions, err2 = api_client.list_excursions(d["id"])
            if err2:
                continue
            for e in excursions or []:
                regs, _ = api_client.list_excursion_registrations(e["id"])
                result.append({
                    "id": e["id"], "kind": "excursion", "type": "excursion",
                    "name": e["name"], "location": e.get("provider_name") or "-",
                    "time": f"{_fmt_time(e.get('gathering_time'))} - {_fmt_time(e.get('return_time'))}",
                    "capacity": e.get("capacity") or 0,
                    "registered": len(regs or []),
                    "price": float(e.get("price") or 0),
                })
    return result


def _my_registration_for(passenger_id, kind, item_id):
    """Tìm bản ghi Registration của passenger này cho đúng activity/excursion
    đang xem - dùng để biết đã đăng ký/check-in chưa và lấy registration_id
    để hủy/check-in."""
    regs, err = api_client.list_passenger_registrations(passenger_id)
    if err:
        return None
    for r in regs or []:
        if kind == "activity" and r.get("activity_id") == item_id:
            return r
        if kind == "excursion" and r.get("excursion_id") == item_id:
            return r
    return None


@passenger_bp.route("/activities")
@login_required
@passenger_access
def activities():
    cruise, passenger = _current_cruise_and_passenger()
    filter_type = request.args.get("filter", "all")
    if not cruise:
        return render_template("passenger/activities.html", activities=[], filter_type=filter_type,
                                registrations=set(), page_title="Hoạt động & Tham quan bờ")

    items = _load_all_activities_and_excursions(cruise)
    if filter_type == "free":
        items = [a for a in items if a["price"] == 0]
    elif filter_type == "paid":
        items = [a for a in items if a["price"] > 0]

    return render_template(
        "passenger/activities.html",
        activities=items,
        filter_type=filter_type,
        registrations=set(),  # đơn giản hoá: badge "đã đăng ký" tính theo is_registered ở trang chi tiết
        page_title="Hoạt động & Tham quan bờ",
    )


@passenger_bp.route("/activities/<string:kind>/<int:item_id>")
@login_required
@passenger_access
def activity_detail(kind, item_id):
    cruise, passenger = _current_cruise_and_passenger()
    items = _load_all_activities_and_excursions(cruise) if cruise else []
    activity = next((a for a in items if a["kind"] == kind and a["id"] == item_id), None)
    if not activity:
        flash("Không tìm thấy hoạt động này.", "danger")
        return redirect(url_for("passenger.activities"))

    my_reg = _my_registration_for(passenger["id"], kind, item_id) if passenger else None
    is_registered = my_reg is not None and my_reg["status"] in ("registered", "checked_in")
    is_checked_in = my_reg is not None and my_reg["status"] == "checked_in"
    is_full = activity["registered"] >= activity["capacity"] if activity["capacity"] else False

    return render_template(
        "passenger/activity_detail.html",
        activity=activity,
        is_registered=is_registered,
        is_checked_in=is_checked_in,
        registration_id=my_reg["id"] if my_reg else None,
        is_full=is_full,
        page_title=activity["name"],
    )


@passenger_bp.route("/activities/<string:kind>/<int:item_id>/register", methods=["POST"])
@login_required
@passenger_access
def register_activity(kind, item_id):
    cruise, passenger = _current_cruise_and_passenger()
    if not passenger:
        return redirect(url_for("passenger.activities"))

    activity_id = item_id if kind == "activity" else None
    excursion_id = item_id if kind == "excursion" else None

    result, err = api_client.register_activity(passenger["id"], activity_id=activity_id, excursion_id=excursion_id)
    if err:
        # Backend trả đúng message MSG01 khi vượt sức chứa (BR-02)
        flash(err, "danger")
    else:
        flash("Đăng ký hoạt động thành công.", "success")
    return redirect(url_for("passenger.activity_detail", kind=kind, item_id=item_id))


@passenger_bp.route("/checkin")
@login_required
@passenger_access
def checkin():
    cruise, passenger = _current_cruise_and_passenger()
    if not passenger:
        return render_template("passenger/checkin.html", passenger={"name": "-", "cabin": "-", "card_id": "-"},
                                page_title="Mã QR check-in")
    p = _passenger_view_model(passenger)
    return render_template("passenger/checkin.html", passenger=p, page_title="Mã QR check-in")


@passenger_bp.route("/bill")
@login_required
@passenger_access
def bill():
    cruise, passenger = _current_cruise_and_passenger()
    if not passenger:
        return render_template("passenger/bill.html", passenger={"balance": 0}, transactions=[],
                                total_spent=0, page_title="Chi phí phát sinh")

    p = _passenger_view_model(passenger)
    transactions, err = api_client.list_passenger_transactions(passenger["id"])
    transactions = transactions or []
    total_spent = sum(float(t["amount"]) for t in transactions)

    view_transactions = [{
        "id": t["id"], "item": t.get("description") or "-",
        "amount": float(t["amount"]), "time": (t.get("created_at") or "")[:16],
        "sync_status": t["sync_status"],
    } for t in transactions]

    return render_template(
        "passenger/bill.html", passenger=p, transactions=view_transactions,
        total_spent=total_spent, page_title="Chi phí phát sinh",
    )


@passenger_bp.route("/notifications")
@login_required
@passenger_access
def notifications():
    cruise, passenger = _current_cruise_and_passenger()
    items = []
    if passenger and cruise:
        items, err = api_client.list_passenger_notifications(passenger["id"], cruise_id=cruise["id"])
        if err:
            flash(f"Lỗi tải thông báo: {err}", "danger")
            items = []

    view = [{
        "id": n["id"], "priority": n["priority"],
        "time": (n.get("created_at") or "")[:16],
        "title": n["title"], "content": n.get("content") or "",
    } for n in (items or [])]

    return render_template("passenger/notifications.html", notifications=view, page_title="Thông báo")


@passenger_bp.route("/my-registrations")
@login_required
@passenger_access
def my_registrations():
    """UC: Xem trạng thái đăng ký + lịch sử đăng ký/check-in của bản thân."""
    cruise, passenger = _current_cruise_and_passenger()
    if not passenger:
        return render_template("passenger/my_registrations.html", registrations=[], page_title="Đăng ký của tôi")

    regs, err = api_client.list_passenger_registrations(passenger["id"])
    if err:
        flash(f"Lỗi tải danh sách đăng ký: {err}", "danger")
        regs = []

    items = _load_all_activities_and_excursions(cruise) if cruise else []
    item_map = {(i["kind"], i["id"]): i for i in items}

    view = []
    for r in regs or []:
        if r.get("activity_id"):
            kind, item_id = "activity", r["activity_id"]
        else:
            kind, item_id = "excursion", r["excursion_id"]
        info = item_map.get((kind, item_id), {"name": "(Hoạt động đã xoá)", "time": "-", "location": "-"})
        view.append({
            "registration_id": r["id"],
            "kind": kind, "item_id": item_id,
            "name": info["name"], "time": info.get("time", "-"), "location": info.get("location", "-"),
            "status": r["status"],
        })

    return render_template("passenger/my_registrations.html", registrations=view, page_title="Đăng ký của tôi")


@passenger_bp.route("/registrations/<int:registration_id>/cancel", methods=["POST"])
@login_required
@passenger_access
def cancel_registration_route(registration_id):
    """Hủy đăng ký (nếu chính sách cho phép - hiện backend luôn cho phép hủy
    khi còn ở trạng thái 'registered', chưa check-in)."""
    result, err = api_client.cancel_registration(registration_id)
    if err:
        flash(f"Không thể hủy đăng ký: {err}", "danger")
    else:
        flash("Đã hủy đăng ký thành công.", "info")
    return redirect(url_for("passenger.my_registrations"))


@passenger_bp.route("/registrations/<int:registration_id>/checkin", methods=["POST"])
@login_required
@passenger_access
def self_checkin(registration_id):
    """Hành khách tự check-in qua app (phương thức 'qr' - mô phỏng quét mã
    QR cá nhân của chính mình khi tới điểm tổ chức hoạt động)."""
    result, err = api_client.checkin(registration_id, method="qr")
    if err:
        # Backend trả đúng message MSG03 nếu không hợp lệ
        flash(err, "danger")
    else:
        # MSG04: "Check-in thành công."
        flash("Check-in thành công.", "success")
    return redirect(url_for("passenger.my_registrations"))


# ==================== MUA DỊCH VỤ (Passenger tự chọn & yêu cầu) ====================
# Lưu ý phạm vi: Passenger chỉ CHỌN và TẠO yêu cầu sử dụng dịch vụ - không
# phải là người quản lý giao dịch bán hàng (đó là việc của POS/Finance).
# Ở mức hiện tại (MVP), yêu cầu được ghi nhận thành 1 Transaction thật ngay
# (chưa có bước NV POS/Finance duyệt) - nếu cần workflow duyệt sau này, có
# thể mở rộng thêm trạng thái riêng.

@passenger_bp.route("/services")
@login_required
@passenger_access
def services():
    """Xem danh sách dịch vụ có thể mua (dùng chung danh mục với POS)."""
    return render_template("passenger/services.html", services=store.POS_ITEMS, page_title="Dịch vụ trên tàu")


@passenger_bp.route("/services/<int:item_id>")
@login_required
@passenger_access
def service_detail(item_id):
    """Xem chi tiết 1 dịch vụ (tên, giá, danh mục)."""
    item = next((i for i in store.POS_ITEMS if i["id"] == item_id), None)
    if not item:
        flash("Không tìm thấy dịch vụ này.", "danger")
        return redirect(url_for("passenger.services"))
    return render_template("passenger/service_detail.html", service=item, page_title=item["name"])


@passenger_bp.route("/services/<int:item_id>/purchase", methods=["POST"])
@login_required
@passenger_access
def purchase_service(item_id):
    """Tạo yêu cầu sử dụng/mua dịch vụ - ghi nhận thành giao dịch thật vào
    tài khoản chi tiêu trên tàu của chính hành khách này."""
    cruise, passenger = _current_cruise_and_passenger()
    item = next((i for i in store.POS_ITEMS if i["id"] == item_id), None)
    if not item or not passenger:
        flash("Không thể thực hiện yêu cầu. Vui lòng thử lại.", "danger")
        return redirect(url_for("passenger.services"))

    tx, err = api_client.create_transaction(
        passenger_id=passenger["id"],
        amount=item["price"],
        description=f"[Khách tự đặt] {item['name']}",
        local_id=str(uuid.uuid4()),
    )
    if err:
        flash(f"Không thể tạo yêu cầu: {err}", "danger")
    else:
        flash(f"Đã ghi nhận yêu cầu sử dụng dịch vụ '{item['name']}'. Nhân viên sẽ phục vụ bạn sớm nhất.", "success")
    return redirect(url_for("passenger.bill"))


# ==================== FEEDBACK (đánh giá Activity/Excursion/Service) ====================

@passenger_bp.route("/feedback/new/<string:kind>/<int:item_id>", methods=["GET", "POST"])
@login_required
@passenger_access
def feedback_new(kind, item_id):
    cruise, passenger = _current_cruise_and_passenger()

    if kind == "service":
        item = next((i for i in store.POS_ITEMS if i["id"] == item_id), None)
        target_name = item["name"] if item else "Dịch vụ"
    else:
        items = _load_all_activities_and_excursions(cruise) if cruise else []
        found = next((a for a in items if a["kind"] == kind and a["id"] == item_id), None)
        target_name = found["name"] if found else "Hoạt động"

    if request.method == "POST":
        if not passenger:
            flash("Không xác định được tài khoản hành khách.", "danger")
            return redirect(url_for("passenger.home"))

        rating = request.form.get("rating", type=int)
        comment = request.form.get("comment", "").strip()

        result, err = api_client.create_feedback(
            passenger_id=passenger["id"], target_type=kind, rating=rating,
            target_id=item_id, target_name=target_name, comment=comment or None,
        )
        if err:
            flash(f"Không thể gửi đánh giá: {err}", "danger")
            return redirect(url_for("passenger.feedback_new", kind=kind, item_id=item_id))

        flash("Cảm ơn bạn đã gửi đánh giá!", "success")
        return redirect(url_for("passenger.my_feedback"))

    return render_template(
        "passenger/feedback_form.html",
        kind=kind, item_id=item_id, target_name=target_name,
        page_title="Gửi đánh giá",
    )


@passenger_bp.route("/feedback")
@login_required
@passenger_access
def my_feedback():
    cruise, passenger = _current_cruise_and_passenger()
    items = []
    if passenger:
        items, err = api_client.list_passenger_feedback(passenger["id"])
        if err:
            flash(f"Lỗi tải đánh giá: {err}", "danger")
            items = []
    return render_template("passenger/my_feedback.html", feedback_list=items or [], page_title="Đánh giá của tôi")


# ==================== TÀI KHOẢN (đăng ký / thông tin cá nhân / đổi mật khẩu) ====================

@passenger_bp.route("/register", methods=["GET", "POST"])
def register():
    """Đăng ký tài khoản Hành khách (self-service, KHÔNG cần đăng nhập).
    Tạo đồng thời: 1) tài khoản đăng nhập cục bộ (users_data.json),
    2) 1 bản ghi Passenger THẬT trên backend/Supabase, rồi liên kết 2 cái
    với nhau qua passenger_id."""
    if current_user.is_authenticated:
        return redirect(url_for("passenger.home"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        if not full_name or not username or not password:
            flash("Vui lòng nhập đầy đủ Họ tên, Tên đăng nhập và Mật khẩu.", "danger")
            return render_template("auth/register_passenger.html")

        if password != password_confirm:
            flash("Mật khẩu xác nhận không khớp.", "danger")
            return render_template("auth/register_passenger.html")

        if len(password) < 6:
            flash("Mật khẩu phải có ít nhất 6 ký tự.", "danger")
            return render_template("auth/register_passenger.html")

        if models.username_exists(username):
            flash("Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác.", "danger")
            return render_template("auth/register_passenger.html")

        cruise, err = api_client.ensure_demo_cruise()
        if err:
            flash(f"Không thể kết nối tới hệ thống backend: {err}", "danger")
            return render_template("auth/register_passenger.html")

        passenger, err = api_client.create_passenger(cruise["id"], full_name)
        if err:
            flash(f"Không thể tạo hồ sơ hành khách: {err}", "danger")
            return render_template("auth/register_passenger.html")

        new_user = models.register_passenger_user(username, password, full_name, passenger["id"])
        login_user(new_user, remember=True)
        flash(f"Đăng ký thành công! Chào mừng {full_name} lên tàu.", "success")
        return redirect(url_for("passenger.home"))

    return render_template("auth/register_passenger.html")


@passenger_bp.route("/profile")
@login_required
@passenger_access
def profile():
    """Xem thông tin tài khoản (username, họ tên, thông tin hành khách thật)."""
    cruise, passenger = _current_cruise_and_passenger()
    p = _passenger_view_model(passenger) if passenger else {"name": current_user.full_name, "cabin": "-", "card_id": "-", "balance": 0}
    return render_template(
        "passenger/profile.html",
        user=current_user,
        passenger=p,
        page_title="Tài khoản của tôi",
    )


@passenger_bp.route("/profile/change-password", methods=["POST"])
@login_required
@passenger_access
def change_password():
    """Đổi mật khẩu."""
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    new_password_confirm = request.form.get("new_password_confirm", "")

    if current_password != current_user.password:
        flash("Mật khẩu hiện tại không đúng.", "danger")
    elif len(new_password) < 6:
        flash("Mật khẩu mới phải có ít nhất 6 ký tự.", "danger")
    elif new_password != new_password_confirm:
        flash("Xác nhận mật khẩu mới không khớp.", "danger")
    else:
        models.update_password(current_user.id, new_password)
        flash("Đổi mật khẩu thành công.", "success")

    return redirect(url_for("passenger.profile"))
