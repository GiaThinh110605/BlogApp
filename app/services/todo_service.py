from typing import Optional, List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.todo import TodoCreate, Todo, TodoUpdate
from app.repositories.todo_repository import TodoRepository


class TodoService:
    """Tầng service: Xử lý business logic"""
    
    def __init__(self):
        self.repo = TodoRepository()
    
    def create_todo(self, todo: TodoCreate, db: Session, owner_id: int) -> Todo:
        """Tạo todo mới"""
        return self.repo.create(todo, db, owner_id)
    
    def get_todo(self, todo_id: int, db: Session, owner_id: int) -> Todo:
        """Lấy todo theo ID của user"""
        todo = self.repo.get_by_id(todo_id, db, owner_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo này không tồn tại")
        return todo
    
    def get_todos(
        self,
        db: Session,
        owner_id: int,
        is_done: Optional[bool] = None,
        q: Optional[str] = None,
        sort: str = "created_at",
        limit: int = 10,
        offset: int = 0
    ) -> dict:
        """Lấy danh sách todos của user với filter"""
        # Validate sort parameter
        if sort not in ["created_at", "-created_at"]:
            raise HTTPException(status_code=400, detail="Tham số sắp xếp không hợp lệ")
        
        items, total = self.repo.get_all(
            db=db,
            owner_id=owner_id,
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
    
    def update_todo(self, todo_id: int, updated_todo: TodoUpdate, db: Session, owner_id: int) -> Todo:
        """Cập nhật todo của user"""
        # Kiểm tra todo tồn tại và thuộc về user
        if not self.repo.exists(todo_id, db, owner_id):
            raise HTTPException(status_code=404, detail="Todo này không tồn tại")
        
        return self.repo.update(todo_id, updated_todo, db, owner_id)
    
    def delete_todo(self, todo_id: int, db: Session, owner_id: int) -> None:
        """Xóa todo của user"""
        if not self.repo.delete(todo_id, db, owner_id):
            raise HTTPException(status_code=404, detail="Todo này không tồn tại")
    
    def complete_todo(self, todo_id: int, db: Session, owner_id: int) -> Todo:
        """Đánh dấu todo của user là hoàn thành"""
        todo = self.repo.complete(todo_id, db, owner_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo này không tồn tại")
        return todo
