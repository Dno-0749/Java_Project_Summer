from flask import Flask, redirect, url_for, session
from flask_login import LoginManager
from config import Config
from blueprints.auth import auth_bp
from blueprints.system_admin import system_admin_bp
from blueprints.operations import operations_bp
from blueprints.coordinator import coordinator_bp
from blueprints.activities import activities_bp
from blueprints.excursions import excursions_bp
from blueprints.finance import finance_bp
from blueprints.pos import pos_bp
from blueprints.passenger import passenger_bp
from models import User, get_user_by_id

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Flask-Login cấu hình
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Vui lòng đăng nhập để tiếp tục."
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Backend is the authentication source of truth. The session keeps the
        # canonical API user so Flask-Login does not need to query Supabase or
        # another database on every request.
        remote = session.get("api_user") or {}
        if str(remote.get("id")) == str(user_id):
            role = str(remote.get("role") or "passenger").lower()
            role_names = {
                "admin": "Quản trị viên hệ thống",
                "operations": "Quản lý vận hành",
                "finance": "Tài chính & Lễ tân",
                "coordinator": "Điều phối lịch trình",
                "activity_manager": "Quản lý hoạt động",
                "sales_staff": "Nhân viên bán hàng & dịch vụ",
                "passenger": "Hành khách",
            }
            return User(
                id=remote.get("id"),
                username=remote.get("username", ""),
                password="",
                full_name=remote.get("full_name") or remote.get("username", ""),
                role=role,
                role_name=role_names.get(role, role),
                status=remote.get("status", "Active"),
                passenger_id=remote.get("passenger_id"),
            )
        return get_user_by_id(user_id)

    # Đăng ký các Blueprint mở rộng theo từng Actor
    app.register_blueprint(auth_bp)
    app.register_blueprint(system_admin_bp)
    app.register_blueprint(operations_bp)
    app.register_blueprint(coordinator_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(excursions_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(passenger_bp)

    # Điều hướng tương thích cho URL cũ nếu có
    @app.route("/admin/dashboard")
    def legacy_dashboard():
        return redirect(url_for("operations.dashboard"))

    return app


if __name__ == "__main__":
    app = create_app()
    print("\n========================================================")
    print("🚢 CRUISE OPS MANAGEMENT - EXPANDABLE MODULAR SYSTEM")
    print("🌐 Web Server chạy tại: http://localhost:5000")
    print("🔑 Danh sách tài khoản chuẩn hóa nhóm 5 thành viên:")
    print("   - nguyenchihai   (123456) -> Quản trị viên & Phân quyền")
    print("   - nguyenhoangphat (123456) -> Quản lý Vận hành")
    print("   - nguyenthithi   (123456) -> Tài chính & Lễ tân")
    print("   - nguyentronghai (123456) -> Điều phối Lịch trình")
    print("   - ledinhquy      (123456) -> Quản lý Hoạt động")
    print("========================================================\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
