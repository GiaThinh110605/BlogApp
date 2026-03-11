from fastapi import APIRouter, Query, Depends
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.todo import TodoCreate, TodoUpdate, Todo
from app.services.todo_service import TodoService
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import User


router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}},
)

# Initialize service
todo_service = TodoService()


@router.post("", status_code=201, response_model=Todo)
def create_todo(
    todo: TodoCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tạo todo mới"""
    return todo_service.create_todo(todo, db, current_user.id)


@router.get("", status_code=200)
def get_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    is_done: Optional[bool] = None,
    q: Optional[str] = None,
    sort: str = "created_at",
    limit: int = Query(10, gt=0),
    offset: int = Query(0, ge=0)
):
    """Lấy danh sách todos của user"""
    return todo_service.get_todos(
        db=db,
        owner_id=current_user.id,
        is_done=is_done,
        q=q,
        sort=sort,
        limit=limit,
        offset=offset
    )


@router.get("/{todo_id}", status_code=200, response_model=Todo)
def get_todo(
    todo_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy todo theo ID của user"""
    return todo_service.get_todo(todo_id, db, current_user.id)


@router.patch("/{todo_id}", status_code=200, response_model=Todo)
def update_todo(
    todo_id: int, 
    updated_todo: TodoUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cập nhật một phần todo của user"""
    return todo_service.update_todo(todo_id, updated_todo, db, current_user.id)


@router.post("/{todo_id}/complete", status_code=200, response_model=Todo)
def complete_todo(
    todo_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Đánh dấu todo của user là hoàn thành"""
    return todo_service.complete_todo(todo_id, db, current_user.id)


@router.delete("/{todo_id}", status_code=204)
def delete_todo(
    todo_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Xóa todo của user"""
    todo_service.delete_todo(todo_id, db, current_user.id)
