from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.soft_delete_service import SoftDeleteService
from app.schemas.todo import Todo
from app.models.user import User

router = APIRouter(prefix="/trash", tags=["trash"])

@router.get("/todos", response_model=list[Todo])
def get_deleted_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Lấy danh sách todos đã bị xóa"""
    service = SoftDeleteService()
    return service.get_deleted_todos(current_user.id, db, skip, limit)

@router.post("/todos/{todo_id}/restore", response_model=Todo)
def restore_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Khôi phục todo từ trash"""
    service = SoftDeleteService()
    return service.restore_todo(todo_id, current_user.id, db)

@router.delete("/todos/{todo_id}")
def permanent_delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Xóa vĩnh viễn todo"""
    service = SoftDeleteService()
    service.permanent_delete_todo(todo_id, current_user.id, db)
    return {"message": "Đã xóa vĩnh viễn todo"}

@router.delete("/empty")
def empty_trash(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dọn trash - xóa vĩnh viễn tất cả"""
    service = SoftDeleteService()
    return service.empty_trash(current_user.id, db)
