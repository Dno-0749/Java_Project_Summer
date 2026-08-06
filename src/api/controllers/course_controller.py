from flask import Blueprint, request, jsonify
from services.todo_service import TodoService
from infrastructure.repositories.todo_repository import TodoRepository
from api.schemas.todo import TodoRequestSchema, TodoResponseSchema
from datetime import datetime

bp = Blueprint('course', __name__, url_prefix='/courses')

# Khởi tạo service và repository (dùng memory, chưa kết nối DB thật)
todo_service = TodoService(TodoRepository())

request_schema = TodoRequestSchema()
response_schema = TodoResponseSchema()

@bp.route('/', methods=['GET'])
def list_todos():
    """
    Get all todos
    ---
    get:
      summary: Get all todos
      tags:
        - Todos
      responses:
        200:
          description: List of todos
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TodoResponse'
    """
    todos = todo_service.list_todos()
    return jsonify(response_schema.dump(todos, many=True)), 200

@bp.route('/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = todo_service.get_todo(todo_id)
    if not todo:
        return jsonify({'message': 'Todo not found'}), 404
    return jsonify(response_schema.dump(todo)), 200

@bp.route('/', methods=['POST'])
def create_todo():
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    now = datetime.utcnow()
    todo = todo_service.create_todo(
        title=data['title'],
        description=data['description'],
        status=data['status'],
        created_at=now,
        updated_at=now
    )
    return jsonify(response_schema.dump(todo)), 201

@bp.route('/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    todo = todo_service.update_todo(
        todo_id=todo_id,
        title=data['title'],
        description=data['description'],
        status=data['status'],
        created_at=datetime.utcnow(),  # Có thể lấy từ DB nếu cần
        updated_at=datetime.utcnow()
    )
    return jsonify(response_schema.dump(todo)), 200

@bp.route('/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo_service.delete_todo(todo_id)
    return '', 204 