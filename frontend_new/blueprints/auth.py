from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import authenticate, get_all_users

auth_bp = Blueprint("auth", __name__)

ROLE_REDIRECT_MAP = {"operations": "operations.dashboard"}

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

        user = authenticate(username, password)
        if user:
            if user.role != "operations":
                flash("Tài khoản này không thuộc Operations Control Center.", "danger")
                return render_template("auth/login.html")

            if not user.is_active:
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
            flash("Tên đăng nhập hoặc mật khẩu không đúng. Mật khẩu mặc định là 123456.", "danger")

    return render_template("auth/login.html", demo_users=get_all_users())


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Bạn đã đăng xuất an toàn khỏi hệ thống.", "info")
    return redirect(url_for("auth.login"))
