# src/api/responses.py

from flask import jsonify

def success_response(data, message="Success"):
    return jsonify({"message": message, "data": data}), 200

def error_response(message="An error occurred", status_code=400):
    return jsonify({"message": message}), status_code

def not_found_response(message="Resource not found"):
    return jsonify({"message": message}), 404

def validation_error_response(errors):
    return jsonify({"message": "Validation errors", "errors": errors}), 422