from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import Config
from blueprints.auth import auth_bp
from blueprints.operations import operations_bp
from blueprints.coordinator import coordinator_bp
from blueprints.activities import activities_bp
from blueprints.excursions import excursions_bp
from blueprints.finance import finance_bp
from blueprints.reports import reports_bp
from models import get_user_by_id

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
        return get_user_by_id(user_id)

    # Operations brand chỉ công khai các luồng vận hành.
    app.register_blueprint(auth_bp)
    app.register_blueprint(operations_bp)
    app.register_blueprint(coordinator_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(excursions_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(reports_bp)

    # Điều hướng tương thích cho URL cũ nếu có
    @app.route("/admin/dashboard")
    def legacy_dashboard():
        return redirect(url_for("operations.dashboard"))

    return app


if __name__ == "__main__":
    app = create_app()
    print("\n========================================================")
    print("🚢 OPSPULSE - OPERATIONS CONTROL CENTER")
    print("🌐 Web Server chạy tại: http://localhost:5000")
    print("🔑 Tài khoản Operations demo: nguyenhoangphat (123456)")
    print("========================================================\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
