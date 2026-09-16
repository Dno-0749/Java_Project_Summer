from datetime import datetime, timedelta, timezone

import jwt
from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import generate_password_hash

from api.schemas.auth import (
    LoginUserRequestSchema,
    RigisterUserRequestSchema,
    RigisterUserResponseSchema,
)
from infrastructure.repositories.auth_repository import AuthRepository
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_repository = AuthRepository()
auth_service = AuthService(auth_repository)
register_request = RigisterUserRequestSchema()
register_response = RigisterUserResponseSchema()
login_request = LoginUserRequestSchema()


def _token_for(user):
    payload = {
        'user_id': user['id'],
        'username': user['username'],
        'role': user.get('role'),
        'exp': datetime.now(timezone.utc) + timedelta(hours=2),
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def decode_token_from_request():
    header = request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        return None, ('Authentication required', 401)
    token = header[7:].strip()
    if not token:
        return None, ('Authentication required', 401)
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256']), None
    except jwt.ExpiredSignatureError:
        return None, ('Authentication token expired', 401)
    except jwt.InvalidTokenError:
        return None, ('Invalid authentication token', 401)


@auth_bp.route('/check_router', methods=['GET'])
def check_router():
    return jsonify({'message': 'Router is working!'}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    errors = login_request.validate(data)
    if errors:
        return jsonify({'error': 'Username and password are required', 'details': errors}), 400

    username = data['username'].strip().lower()
    password = data['password']
    user = auth_service.login(username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    user_data = auth_repository.get_user(user.id)
    if not user_data:
        return jsonify({'error': 'User not found'}), 404

    token = _token_for(user_data)
    return jsonify({
        'access_token': token,
        'token': token,  # backwards compatibility
        'user': user_data,
    }), 200


@auth_bp.route('/me', methods=['GET'])
def me():
    claims, error = decode_token_from_request()
    if error:
        return jsonify({'error': error[0]}), error[1]
    user = auth_repository.get_user(int(claims['user_id']))
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user), 200


@auth_bp.route('/signup', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    errors = register_request.validate(data)
    if errors:
        return jsonify(errors), 400

    username = data.get('username', '').strip().lower()
    password = data.get('password', '')
    passwordconfirm = data.get('passwordconfirm', '')
    email = data.get('email', '').strip().lower()

    if password != passwordconfirm:
        return jsonify({'message': 'Passwords do not match'}), 400
    if auth_service.check_exist(username):
        return jsonify({'message': 'User already exists. Please login.'}), 400

    new_user = auth_service.register(username, generate_password_hash(password), email)
    if not new_user:
        return jsonify({'message': 'Registration failed'}), 500
    return jsonify(register_response.dump(new_user)), 201
