from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.soft_delete_repository import SoftDeleteRepository
from app.models.todo import Todo

class SoftDeleteService:
    def __init__(self):
        self.repo = SoftDeleteRepository()
    
    def get_active_todos(self, user_id: int, db: Session, skip: int = 0, limit: int = 100) -> List[Todo]:
        """Lấy todos đang hoạt động"""
        return self.repo.get_active_todos(user_id, db, skip, limit)
    
    def get_deleted_todos(self, user_id: int, db: Session, skip: int = 0, limit: int = 100) -> List[Todo]:
        """Lấy todos đã bị xóa (trash)"""
        return self.repo.get_deleted_todos(user_id, db, skip, limit)
    
    def soft_delete_todo(self, todo_id: int, user_id: int, db: Session) -> Todo:
        """Chuyển todo vào trash"""
        todo = self.repo.soft_delete_todo(todo_id, user_id, db)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo không tồn tại hoặc đã bị xóa")
        return todo
    
    def restore_todo(self, todo_id: int, user_id: int, db: Session) -> Todo:
        """Khôi phục todo từ trash"""
        todo = self.repo.restore_todo(todo_id, user_id, db)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo không tồn tại trong trash")
        return todo
    
    def permanent_delete_todo(self, todo_id: int, user_id: int, db: Session) -> None:
        """Xóa vĩnh viễn todo"""
        if not self.repo.permanent_delete_todo(todo_id, user_id, db):
            raise HTTPException(status_code=404, detail="Todo không tồn tại trong trash")
    
    def empty_trash(self, user_id: int, db: Session) -> dict:
        """Dọn trash"""
        count = self.repo.empty_trash(user_id, db)
        return {"message": f"Đã xóa vĩnh viễn {count} todo", "count": count}
