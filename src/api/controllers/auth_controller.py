from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from infrastructure.models.user_model import UserModel
from infrastructure.databases.mssql import session
from api.schemas.auth import RigisterUserRequestSchema,RigisterUserResponseSchema
from services.auth_service import AuthService
from infrastructure.repositories.auth_repository import AuthRepository
import jwt
from werkzeug.security import generate_password_hash
from services.supabase_auth_service import authenticate as authenticate_supabase_user, delete_user, list_users
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = AuthService(AuthRepository(session))
register_request = RigisterUserRequestSchema()
register_response = RigisterUserResponseSchema()
@auth_bp.route('/check_router', methods=['GET'])
def check_router():
    """
    Check router
    ---
    get:
      summary: Check router health
      tags:
        - Auth
      responses:
        200:
          description: Router is working
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    return jsonify({'message': 'Router is working!'}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user
    ---
    post:
      summary: Login user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginUserRequest'
      tags:
        - Auth
      responses:
        200:
          description: Successful login
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginUserResponse'
        401:
          description: Invalid credentials
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
    """
    data = request.get_json(silent=True) or {}
    username = data.get('username', '')
    password = data.get('password', '')
    if not username or not password:
      return jsonify({'error': 'Username and password are required'}), 400

    user = authenticate_supabase_user(username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    payload = {
        'user_id': user['id'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token, 'user': user})


@auth_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user_route(user_id):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authentication required'}), 401
    try:
        claims = jwt.decode(
            auth_header[7:],
            current_app.config['SECRET_KEY'],
            algorithms=['HS256'],
        )
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid authentication token'}), 401
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    if str(claims.get('user_id')) == str(user_id):
        return jsonify({'error': 'You cannot delete your own account'}), 400
    if not delete_user(user_id):
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'User deleted'}), 200


@auth_bp.route('/users', methods=['GET'])
def list_users_route():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authentication required'}), 401
    try:
        claims = jwt.decode(
            auth_header[7:],
            current_app.config['SECRET_KEY'],
            algorithms=['HS256'],
        )
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid authentication token'}), 401
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    return jsonify({'users': list_users()}), 200


@auth_bp.route('/signup', methods=['POST'])
def register():
    """
    Register a new user
    ---
    post:
      summary: Register a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RigisterUserRequest'
      tags:
        - Auth
      responses:
        201:
          description: User registered successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RigisterUserResponse'
        400:
          description: Invalid input or user exists
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    data = request.get_json()
    errors = register_request.validate(data)
    if errors:
      return jsonify(errors), 400
    # Lay thong tin tu nguoi dung truyen vao

    # Support JSON body and avoid KeyError by using .get()
    username = data.get('username') if isinstance(data, dict) else None
    password = data.get('password') if isinstance(data, dict) else None
    passwordconfirm = data.get('passwordconfirm') if isinstance(data, dict) else None
    email = data.get('email') if isinstance(data, dict) else None

    if not username or not password or not passwordconfirm or not email:
      return jsonify({'message': 'Missing required fields: username, password, passwordconfirm, email'}), 400

    if password != passwordconfirm:
      return jsonify({'message': 'Passwords do not match'}), 400

    if auth_service.check_exist(username):
      return jsonify({'message': 'User already exists. Please login.'}), 400
    #  vieets theo kien truc clean architecture
    # password_hashed = Str.encode()(password)
    password_hashed =generate_password_hash(password)
    new_user = auth_service.register(username, password_hashed, email)
    if not new_user:
      return jsonify({'message': 'Registration failed'}), 500 
    result = register_response.dump(new_user)
    return jsonify(result), 201

    #     return redirect(url_for('login'))

    # return render_template('register.html')