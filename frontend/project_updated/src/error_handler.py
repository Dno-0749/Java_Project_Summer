# Error handling logic for the Flask application

from flask import jsonify

class CustomError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        self.message = message

    def to_dict(self):
        return {'message': self.message}

def handle_error(error):
    if isinstance(error, CustomError):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    response = jsonify({'message': 'An unexpected error occurred.'})
    response.status_code = 500
    return response

def register_error_handlers(app):
    app.register_error_handler(Exception, handle_error)