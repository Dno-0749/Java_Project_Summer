from flask import Flask, jsonify
from flasgger import Swagger
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy import text

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

from infrastructure.models.activity_model import ActivityModel
from infrastructure.models.activity_registration_model import ActivityRegistrationModel


def create_app():
    app = Flask(__name__)

    Swagger(app)

    app.register_blueprint(todo_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tour_provider_bp)
    app.register_blueprint(shore_excursion_bp)
    app.register_blueprint(activity_schedule_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(activity_registration_bp)

    try:
        init_db(app)

        db = FactoryDatabase.get_database("POSTGREE")

        Base.metadata.create_all(bind=db.engine)

        with db.engine.connect() as connection:
            result = connection.execute(
                text("PRAGMA table_info(activity_registrations)")
            )

            columns = result.fetchall()
            column_names = [column[1] for column in columns]

            if columns:
                if "rating" not in column_names:
                    connection.execute(
                        text(
                            "ALTER TABLE activity_registrations "
                            "ADD COLUMN rating INTEGER"
                        )
                    )

                if "feedback" not in column_names:
                    connection.execute(
                        text(
                            "ALTER TABLE activity_registrations "
                            "ADD COLUMN feedback VARCHAR(1000)"
                        )
                    )

                connection.commit()

        print("DATABASE INITIALIZED SUCCESSFULLY")

    except Exception as e:
        print(f"DATABASE INITIALIZATION ERROR: {e}")

    middleware(app)

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
                view_func = app.view_functions[rule.endpoint]

                print(
                    f"Adding path: {rule.rule} -> {view_func}"
                )

                try:
                    spec.path(view=view_func)
                except Exception as e:
                    print(
                        f"Swagger path error {rule.rule}: {e}"
                    )

    @app.route("/swagger.json")
    def swagger_json():
        return jsonify(spec.to_dict())

    return app


if __name__ == "__main__":
    app = create_app()

    app.run(
        host="0.0.0.0",
        port=9999,
        debug=True
    )