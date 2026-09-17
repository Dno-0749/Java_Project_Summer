from api.controllers.auth_controller import auth_bp
from api.controllers.operations_controller import bp as operations_bp
from api.controllers.todo_controller import bp as todo_bp
from api.controllers.course_controller import bp as course_bp
from api.controllers.checkin_controller import bp as checkin_bp
from api.controllers.tour_provider_controller import bp as tour_provider_bp
from api.controllers.shore_excursion_controller import bp as shore_excursion_bp
from api.controllers.activity_schedule_controller import bp as activity_schedule_bp
from api.controllers.activity_controller import bp as activity_bp
from api.controllers.activity_registration_controller import bp as activity_registration_bp


def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(operations_bp)
    app.register_blueprint(todo_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(checkin_bp)
    app.register_blueprint(tour_provider_bp)
    app.register_blueprint(shore_excursion_bp)
    app.register_blueprint(activity_schedule_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(activity_registration_bp)
