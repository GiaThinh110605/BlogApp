from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from app.models.todo import Todo

class SoftDeleteRepository:
    """Repository với soft delete support"""
    
    @staticmethod
    def get_active_todos(user_id: int, db: Session, skip: int = 0, limit: int = 100) -> List[Todo]:
        """Lấy todos chưa bị xóa"""
        return db.query(Todo).filter(
            and_(
                Todo.owner_id == user_id,
                Todo.deleted_at.is_(None)
            )
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_deleted_todos(user_id: int, db: Session, skip: int = 0, limit: int = 100) -> List[Todo]:
        """Lấy todos đã bị xóa (trash)"""
        return db.query(Todo).filter(
            and_(
                Todo.owner_id == user_id,
                Todo.deleted_at.isnot(None)
            )
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def soft_delete_todo(todo_id: int, user_id: int, db: Session) -> Optional[Todo]:
        """Soft delete todo"""
        todo = db.query(Todo).filter(
            and_(
                Todo.id == todo_id,
                Todo.owner_id == user_id,
                Todo.deleted_at.is_(None)
            )
        ).first()
        
        if todo:
            todo.deleted_at = datetime.utcnow()
            db.commit()
            db.refresh(todo)
        
        return todo
    
    @staticmethod
    def restore_todo(todo_id: int, user_id: int, db: Session) -> Optional[Todo]:
        """Khôi phục todo từ trash"""
        todo = db.query(Todo).filter(
            and_(
                Todo.id == todo_id,
                Todo.owner_id == user_id,
                Todo.deleted_at.isnot(None)
            )
        ).first()
        
        if todo:
            todo.deleted_at = None
            db.commit()
            db.refresh(todo)
        
        return todo
    
    @staticmethod
    def permanent_delete_todo(todo_id: int, user_id: int, db: Session) -> bool:
        """Xóa vĩnh viễn todo"""
        todo = db.query(Todo).filter(
            and_(
                Todo.id == todo_id,
                Todo.owner_id == user_id,
                Todo.deleted_at.isnot(None)  # Chỉ xóa vĩnh viễn todo đã ở trash
            )
        ).first()
        
        if todo:
            db.delete(todo)
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def empty_trash(user_id: int, db: Session) -> int:
        """Xóa vĩnh viễn tất cả todos trong trash"""
        todos = db.query(Todo).filter(
            and_(
                Todo.owner_id == user_id,
                Todo.deleted_at.isnot(None)
            )
        ).all()
        
        count = len(todos)
        for todo in todos:
            db.delete(todo)
        
        db.commit()
        return count
