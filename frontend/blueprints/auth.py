import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from config import Config
from models import User

auth_bp = Blueprint("auth", __name__)

# Bản đồ điều hướng thông minh theo chuyên môn của từng vai trò
ROLE_REDIRECT_MAP = {
    "admin": "system_admin.users",              # Nguyễn Chí Hải -> Trang Quản lý & Phân quyền
    "operations": "operations.dashboard",       # Nguyễn Hoàng Phát -> Dashboard Vận hành
    "coordinator": "coordinator.itinerary",     # Nguyễn Trọng Hải -> Quản lý Lịch trình
    "activity_manager": "activities.activities",# Lê Đình Quý -> Quản lý Hoạt động trên tàu
    "finance": "finance.finance",               # Nguyễn Thị Thi -> Tài chính & Đối soát
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

        user = None
        try:
            payload = json.dumps({"username": username, "password": password}).encode("utf-8")
            backend_request = Request(
                f"{Config.API_BASE_URL}/auth/login",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(backend_request, timeout=8) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                user_data = response_data.get("user")
            if user_data:
                user = User.from_api(user_data)
                session["authenticated_user"] = user.to_dict()
                session["backend_token"] = response_data.get("token")
        except (HTTPError, URLError, TimeoutError, ValueError):
            flash("Không thể kết nối máy chủ xác thực. Vui lòng thử lại sau.", "danger")

        if user:
            if not user.is_active:
                flash("Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ Quản trị viên.", "danger")
                return render_template("auth/login.html")

            login_user(user, remember=True)
            flash(f"Xin chào {user.full_name}! Đã đăng nhập với vai trò {user.role_name}.", "success")

            # Ưu tiên trang tiếp theo (nếu có tham số next), nếu không tự động nhảy vào trang chuyên môn
            next_page = request.args.get("next")
            if next_page and not next_page.startswith("/login"):
                return redirect(next_page)

            target_endpoint = ROLE_REDIRECT_MAP.get(user.role, "operations.dashboard")
            return redirect(url_for(target_endpoint))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng. Mật khẩu mặc định là 123456.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("authenticated_user", None)
    session.pop("backend_token", None)
    flash("Bạn đã đăng xuất an toàn khỏi hệ thống.", "info")
    return redirect(url_for("auth.login"))
