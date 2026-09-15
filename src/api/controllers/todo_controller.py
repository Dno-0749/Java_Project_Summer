from flask import Blueprint, request, jsonify
from services.todo_service import TodoService
from infrastructure.repositories.todo_repository import TodoRepository
from api.schemas.todo import TodoRequestSchema, TodoResponseSchema
from datetime import datetime
from infrastructure.databases.mssql import session
bp = Blueprint('todo', __name__, url_prefix='/todos')

todo_service = TodoService(TodoRepository(session))

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
    """
    Get todo by id
    ---
    get:
      summary: Get todo by id
      parameters:
        - name: todo_id
          in: path
          required: true
          schema:
            type: integer
          description: ID của todo cần lấy
      tags:
        - Todos
      responses:
        200:
          description: object of todo
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TodoResponse'
        404:
          description: Todo not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    todo = todo_service.get_todo(todo_id)
    if not todo:
        return jsonify({'message': 'Todo not found'}), 404
    return jsonify(response_schema.dump(todo)), 200


@bp.route('/', methods=['POST'])
def create_todo():
    """
    Create a new todo
    ---
    post:
      summary: Create a new todo
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TodoRequest'
      tags:
        - Todos
      responses:
        201:
          description: Todo created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TodoResponse'
        400:
          description: Invalid input
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
    """
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
    """
    Update a todo by id
    ---
    put:
      summary: Update a todo by id
      parameters:
        - name: todo_id
          in: path
          required: true
          schema:
            type: integer
          description: ID của todo cần cập nhật
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TodoRequest'
      tags:
        - Todos
      responses:
        200:
          description: Todo updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TodoResponse'
        400:
          description: Invalid input
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
        404:
          description: Todo not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    data = request.get_json()
    errors = request_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    todo = todo_service.update_todo(
        todo_id=todo_id,
        title=data['title'],
        description=data['description'],
        status=data['status'],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    return jsonify(response_schema.dump(todo)), 200

@bp.route('/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """
    Delete a todo by id
    ---
    delete:
      summary: Delete a todo by id
      parameters:
        - name: todo_id
          in: path
          required: true
          schema:
            type: integer
          description: ID của todo cần xóa
      tags:
        - Todos
      responses:
        204:
          description: Todo deleted successfully
        404:
          description: Todo not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    todo_service.delete_todo(todo_id)
    return '', 204