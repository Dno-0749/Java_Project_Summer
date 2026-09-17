from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import get_all_users, add_user, toggle_user_status, delete_user, ROLE_DISPLAY_NAMES, slugify_username
from supabase_client import is_supabase_configured
import api_client

system_admin_bp = Blueprint("system_admin", __name__, url_prefix="/system")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != "admin":
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function

@system_admin_bp.route("/users")
@login_required
@admin_required
def users():
    user_list, error = api_client.admin_users()
    if error:
        flash(error, "danger")
        user_list = []
    return render_template(
        "system_admin/users.html",
        users=user_list,
        role_options=ROLE_DISPLAY_NAMES,
        page_title="Quản lý Người dùng & Phân quyền"
    )

@system_admin_bp.route("/users/add", methods=["POST"])
@login_required
@admin_required
def add_user_route():
    full_name = request.form.get("full_name", "").strip()
    role = request.form.get("role", "").strip()
    custom_username = request.form.get("username", "").strip()

    if not full_name:
        flash("Vui lòng nhập họ và tên nhân viên.", "danger")
        return redirect(url_for("system_admin.users"))

    if role not in ROLE_DISPLAY_NAMES:
        flash("Vai trò không hợp lệ.", "danger")
        return redirect(url_for("system_admin.users"))

    new_user, error = api_client.create_admin_user({
        "full_name": full_name,
        "username": custom_username or slugify_username(full_name),
        "role": role,
    })
    if error:
        flash(error, "danger")
        return redirect(url_for("system_admin.users"))
    flash(
        f"Cấp tài khoản thành công cho {new_user['full_name']}! "
        f"Tên đăng nhập: [{new_user['username']}] | Mật khẩu mặc định: [123456] | Vai trò: [{new_user['role']}].",
        "success"
    )
    return redirect(url_for("system_admin.users"))

@system_admin_bp.route("/users/<user_id>/toggle-status", methods=["POST"])
@login_required
@admin_required
def toggle_status(user_id):
    if str(current_user.id) == str(user_id):
        flash("Bạn không thể tự vô hiệu hóa tài khoản của chính mình!", "warning")
        return redirect(url_for("system_admin.users"))

    user, error = api_client.update_admin_user(user_id, {
        "status": request.form.get("status", "Inactive")
    })
    if user and not error:
        status_text = "kích hoạt" if user.get("status") == "Active" else "vô hiệu hóa"
        flash(f"Đã {status_text} tài khoản {user.get('full_name')} ({user.get('username')}).", "info")
    elif error:
        flash(error, "danger")
    else:
        flash("Không tìm thấy người dùng.", "danger")
    return redirect(url_for("system_admin.users"))


@system_admin_bp.route("/users/<user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user_route(user_id):
    if str(current_user.id) == str(user_id):
        flash("Bạn không thể tự xóa tài khoản của chính mình!", "warning")
        return redirect(url_for("system_admin.users"))

    user, error = api_client.delete_admin_user(user_id)
    if not error:
        flash("Đã xóa tài khoản.", "info")
    elif error:
        flash(error, "danger")
    else:
        flash("Không tìm thấy người dùng.", "danger")
    return redirect(url_for("system_admin.users"))

@system_admin_bp.route("/settings")
@login_required
@admin_required
def settings():
    return render_template("system_admin/settings.html", page_title="Cấu hình Hệ thống")


@system_admin_bp.route("/admin")
@login_required
@admin_required
def admin_control_panel():
    catalog, catalog_error = api_client.admin_catalog()
    ships, ships_error = api_client.admin_ships()
    areas, areas_error = api_client.admin_areas()
    policies, policies_error = api_client.admin_policies()
    devices, devices_error = api_client.admin_devices()
    logs, logs_error = api_client.admin_logs(100)
    for error in (catalog_error, ships_error, areas_error, policies_error, devices_error, logs_error):
        if error:
            flash(error, "danger")
    return render_template(
        "system_admin/admin.html",
        catalog=catalog or {},
        ships=ships or [],
        areas=areas or [],
        policies=policies or [],
        devices=devices or [],
        logs=logs or [],
        page_title="Quản trị hệ thống",
    )


@system_admin_bp.route("/admin/ships", methods=["POST"])
@login_required
@admin_required
def admin_create_ship():
    _, error = api_client.create_admin_ship({
        "name": request.form.get("name", "").strip(),
        "code": request.form.get("code", "").strip(),
        "status": request.form.get("status", "active"),
        "capacity": request.form.get("capacity", type=int),
        "description": request.form.get("description", "").strip(),
    })
    flash(error or "Đã tạo tàu.", "danger" if error else "success")
    return redirect(url_for("system_admin.admin_control_panel"))


@system_admin_bp.route("/admin/ships/<int:ship_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete_ship(ship_id):
    _, error = api_client.delete_admin_ship(ship_id)
    flash(error or "Đã xóa tàu.", "danger" if error else "success")
    return redirect(url_for("system_admin.admin_control_panel"))


@system_admin_bp.route("/admin/areas", methods=["POST"])
@login_required
@admin_required
def admin_create_area():
    _, error = api_client.create_admin_area({
        "name": request.form.get("name", "").strip(),
        "deck": request.form.get("deck", "").strip(),
        "status": request.form.get("status", "active"),
        "description": request.form.get("description", "").strip(),
    })
    flash(error or "Đã tạo khu vực trên tàu.", "danger" if error else "success")
    return redirect(url_for("system_admin.admin_control_panel"))


@system_admin_bp.route("/admin/areas/<int:area_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete_area(area_id):
    _, error = api_client.delete_admin_area(area_id)
    flash(error or "Đã xóa khu vực.", "danger" if error else "success")
    return redirect(url_for("system_admin.admin_control_panel"))


@system_admin_bp.route("/admin/policies/<policy_key>", methods=["POST"])
@login_required
@admin_required
def admin_update_policy(policy_key):
    _, error = api_client.update_admin_policy(policy_key, {
        "policy_value": request.form.get("policy_value", "").strip(),
    })
    flash(error or "Đã cập nhật chính sách.", "danger" if error else "success")
    return redirect(url_for("system_admin.admin_control_panel"))


@system_admin_bp.route("/admin/devices", methods=["POST"])
@login_required
@admin_required
def admin_create_device():
    _, error = api_client.create_admin_device({
        "device_code": request.form.get("device_code", "").strip(),
        "device_type": request.form.get("device_type", "qr_scanner"),
        "status": request.form.get("status", "active"),
        "location": request.form.get("location", "").strip(),
        "assigned_to": request.form.get("assigned_to", "").strip(),
    })
    flash(error or "Đã đăng ký thiết bị.", "danger" if error else "success")
    return redirect(url_for("system_admin.admin_control_panel"))


@system_admin_bp.route("/admin/devices/<int:device_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete_device(device_id):
    _, error = api_client.delete_admin_device(device_id)
    flash(error or "Đã xóa thiết bị.", "danger" if error else "success")
    return redirect(url_for("system_admin.admin_control_panel"))
