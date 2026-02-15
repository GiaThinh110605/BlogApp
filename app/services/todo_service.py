from typing import Optional, List
from fastapi import HTTPException
from schemas.todo import TodoCreate, Todo, TodoUpdate
from repositories.todo_repository import TodoRepository


class TodoService:
    """Tầng service: Xử lý business logic"""
    
    def __init__(self):
        self.repo = TodoRepository()
    
    def create_todo(self, todo: TodoCreate) -> Todo:
        """Tạo todo mới"""
        # Validate: Id không được trùng
        if self.repo.exists(todo.id):
            raise HTTPException(status_code=400, detail="Id đã tồn tại")
        
        return self.repo.create(todo)
    
    def get_todo(self, todo_id: int) -> Todo:
        """Lấy todo theo ID"""
        todo = self.repo.get_by_id(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo này không tồn tại")
        return todo
    
    def get_todos(
        self,
        is_done: Optional[bool] = None,
        q: Optional[str] = None,
        sort: str = "created_at",
        limit: int = 10,
        offset: int = 0
    ) -> dict:
        """Lấy danh sách todos với filter"""
        # Validate sort parameter
        if sort not in ["created_at", "-created_at"]:
            raise HTTPException(status_code=400, detail="Tham số sắp xếp không hợp lệ")
        
        items, total = self.repo.get_all(
            is_done=is_done,
            search=q,
            sort=sort,
            limit=limit,
            offset=offset
        )
        
        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def update_todo(self, todo_id: int, updated_todo: TodoUpdate) -> Todo:
        """Cập nhật todo"""
        # Lấy todo hiện tại
        todo = self.repo.get_by_id(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo này không tồn tại")
        
        # Cập nhật dữ liệu
        updated = Todo(
            id=todo.id,
            title=updated_todo.title,
            is_done=updated_todo.is_done,
            created_at=todo.created_at
        )
        
        return self.repo.update(todo_id, updated)
    
    def delete_todo(self, todo_id: int) -> None:
        """Xóa todo"""
        if not self.repo.delete(todo_id):
            raise HTTPException(status_code=404, detail="Todo này không tồn tại")
