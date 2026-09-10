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
from models import User

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
        user_data = session.get("authenticated_user")
        if user_data and str(user_data.get("id")) == str(user_id):
            return User.from_dict(user_data)
        return None

    # Đăng ký các Blueprint mở rộng theo từng Actor
    app.register_blueprint(auth_bp)
    app.register_blueprint(system_admin_bp)
    app.register_blueprint(operations_bp)
    app.register_blueprint(coordinator_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(excursions_bp)
    app.register_blueprint(finance_bp)

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
