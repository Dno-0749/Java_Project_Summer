from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from models import get_all_users, add_user, toggle_user_status, ROLE_DISPLAY_NAMES, slugify_username

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
    user_list = get_all_users()
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

    new_user = add_user(full_name=full_name, role=role, custom_username=custom_username)
    flash(
        f"✅ Cấp tài khoản thành công cho {new_user.full_name}! "
        f"Tên đăng nhập: [{new_user.username}] | Mật khẩu mặc định: [123456] | Vai trò: [{new_user.role_name}].",
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

    user = toggle_user_status(user_id)
    if user:
        status_text = "kích hoạt" if user.is_active else "vô hiệu hóa"
        flash(f"Đã {status_text} tài khoản {user.full_name} ({user.username}).", "info")
    else:
        flash("Không tìm thấy người dùng.", "danger")
    return redirect(url_for("system_admin.users"))

@system_admin_bp.route("/settings")
@login_required
@admin_required
def settings():
    return render_template("system_admin/settings.html", page_title="Cấu hình Hệ thống")
