from domain.models.todo import Todo
from domain.models.itodo_repository import ITodoRepository
from typing import List, Optional

class TodoService:
    def __init__(self, repository: ITodoRepository):
        self.repository = repository

    def create_todo(self, title: str, description: str, status: str, created_at, updated_at) -> Todo:
        todo = Todo(id=None, title=title, description=description, status=status, created_at=created_at, updated_at=updated_at)
        return self.repository.add(todo)

    def get_todo(self, todo_id: int) -> Optional[Todo]:
        return self.repository.get_by_id(todo_id)

    def list_todos(self) -> List[Todo]:
        return self.repository.list()

    def update_todo(self, todo_id: int, title: str, description: str, status: str, created_at, updated_at) -> Todo:
        todo = Todo(id=todo_id, title=title, description=description, status=status, created_at=created_at, updated_at=updated_at)
        return self.repository.update(todo)

    def delete_todo(self, todo_id: int) -> None:
        self.repository.delete(todo_id) 