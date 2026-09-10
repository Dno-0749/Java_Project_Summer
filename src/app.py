from flask import Flask, jsonify

from api.swagger import spec

from api.controllers.todo_controller import bp as todo_bp
from api.controllers.auth_controller import auth_bp
from api.controllers.tour_provider_controller import bp as tour_provider_bp
from api.controllers.shore_excursion_controller import bp as shore_excursion_bp
from api.controllers.activity_schedule_controller import bp as activity_schedule_bp
from api.controllers.activity_controller import bp as activity_bp
from api.controllers.activity_registration_controller import bp as activity_registration_bp

from api.middleware import middleware
from infrastructure.databases import init_db

from infrastructure.databases.factory_database import FactoryDatabase
from infrastructure.databases.base import Base

# Import model để SQLAlchemy đăng ký các bảng
from infrastructure.models.activity_model import ActivityModel
from infrastructure.models.activity_registration_model import ActivityRegistrationModel

from flasgger import Swagger
from flask_swagger_ui import get_swaggerui_blueprint


def create_app():
    app = Flask(__name__)

    # Swagger
    Swagger(app)

    # =========================
    # REGISTER BLUEPRINTS
    # =========================

    app.register_blueprint(todo_bp)
    app.register_blueprint(auth_bp)

    app.register_blueprint(tour_provider_bp)
    app.register_blueprint(shore_excursion_bp)

    app.register_blueprint(activity_schedule_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(activity_registration_bp)

    # =========================
    # DATABASE
    # =========================

    try:
        init_db(app)

        # Lấy database hiện tại
        db = FactoryDatabase.get_database("POSTGREE")

        # Tạo tất cả bảng còn thiếu
        Base.metadata.create_all(
            bind=db.engine
        )

        print("Database initialized successfully.")

    except Exception as e:
        print(f"Error initializing database: {e}")

    # =========================
    # SWAGGER UI
    # =========================

    SWAGGER_URL = "/docs"
    API_URL = "/swagger.json"

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            "app_name": "Activity & Shore Excursion API"
        }
    )

    app.register_blueprint(
        swaggerui_blueprint,
        url_prefix=SWAGGER_URL
    )

    # =========================
    # MIDDLEWARE
    # =========================

    middleware(app)

    # =========================
    # REGISTER SWAGGER PATHS
    # =========================

    with app.test_request_context():

        for rule in app.url_map.iter_rules():

            if rule.endpoint.startswith((
                "todo.",
                "course.",
                "user.",
                "auth.",
                "tour_provider.",
                "shore_excursion.",
                "activity_schedule.",
                "activities_api.",
                "activity_registration."
            )):

                view_func = app.view_functions[
                    rule.endpoint
                ]

                print(
                    f"Adding path: "
                    f"{rule.rule} -> "
                    f"{view_func}"
                )

                try:
                    spec.path(
                        view=view_func
                    )
                except Exception as e:
                    print(
                        f"Swagger path error "
                        f"{rule.rule}: {e}"
                    )

    # =========================
    # SWAGGER JSON
    # =========================

    @app.route("/swagger.json")
    def swagger_json():
        return jsonify(
            spec.to_dict()
        )

    return app


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":

    app = create_app()

    app.run(
        host="0.0.0.0",
        port=9999,
        debug=True
    )