from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models import User, get_all_users, get_user_by_id, ROLE_DISPLAY_NAMES
from api_client import login as api_login, get_current_user

auth_bp = Blueprint("auth", __name__)

# Bản đồ điều hướng thông minh theo chuyên môn của từng vai trò
ROLE_REDIRECT_MAP = {
    "admin": "system_admin.users",              # Nguyễn Chí Hải -> Trang Quản lý & Phân quyền
    "operations": "operations.dashboard",       # Nguyễn Hoàng Phát -> Dashboard Vận hành
    "coordinator": "coordinator.itinerary",     # Nguyễn Trọng Hải -> Quản lý Lịch trình
    "activity_manager": "activities.activities",# Lê Đình Quý -> Quản lý Hoạt động trên tàu
    "finance": "finance.finance",               # Nguyễn Thị Thi -> Tài chính & Đối soát
    "sales_staff": "pos.sales",                  # Nhân viên POS -> Màn bán hàng
    "passenger": "passenger.home",               # Hành khách -> Trang chủ mobile
}

@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        target_endpoint = ROLE_REDIRECT_MAP.get(current_user.role, "operations.dashboard")
        return redirect(url_for(target_endpoint))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        target_endpoint = ROLE_REDIRECT_MAP.get(current_user.role, "operations.dashboard")
        return redirect(url_for(target_endpoint))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        auth_data, api_error = api_login(username, password)
        user = None
        if not api_error and auth_data:
            remote = auth_data.get("user") or {}
            session["access_token"] = auth_data.get("access_token") or auth_data.get("token")
            session["api_user"] = remote

            # Keep FE-only presentation fields (full_name/role_name) from the
            # existing local catalogue, while credentials and identity come
            # from the backend. This avoids a second password authority.
            for candidate in get_all_users():
                if candidate.username == username:
                    user = candidate
                    break
            if user is None:
                role = remote.get("role", "passenger").lower()
                user = User(
                    id=remote.get("id"),
                    username=remote.get("username", username),
                    password="",
                    full_name=remote.get("username", username),
                    role=role,
                    status="Active",
                )
            user.id = str(remote.get("id", user.id))
            user.username = remote.get("username", user.username)
            user.role = remote.get("role", user.role).lower()
            user.role_name = ROLE_DISPLAY_NAMES.get(user.role, user.role)
            user.password = ""

        if user:
            if not user.is_active:
                session.pop("access_token", None)
                session.pop("api_user", None)
                flash("Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ Quản trị viên.", "danger")
                return render_template("auth/login.html", demo_users=get_all_users())

            login_user(user, remember=True)
            flash(f"Xin chào {user.full_name}! Đã đăng nhập với vai trò {user.role_name}.", "success")

            # Ưu tiên trang tiếp theo (nếu có tham số next), nếu không tự động nhảy vào trang chuyên môn
            next_page = request.args.get("next")
            if next_page and not next_page.startswith("/login"):
                return redirect(next_page)

            target_endpoint = ROLE_REDIRECT_MAP.get(user.role, "operations.dashboard")
            return redirect(url_for(target_endpoint))
        else:
            flash(api_error or "Tên đăng nhập hoặc mật khẩu không đúng.", "danger")

    return render_template("auth/login.html", demo_users=get_all_users())


@auth_bp.route("/logout")
@login_required
def logout():
    session.pop("access_token", None)
    session.pop("api_user", None)
    logout_user()
    flash("Bạn đã đăng xuất an toàn khỏi hệ thống.", "info")
    return redirect(url_for("auth.login"))
