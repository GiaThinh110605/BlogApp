from fastapi import APIRouter, Query, Depends
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.todo import TodoCreate, TodoUpdate, Todo
from app.services.todo_service import TodoService
from app.core.database import get_db


router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}},
)

# Initialize service
todo_service = TodoService()


@router.post("", status_code=201, response_model=Todo)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """Tạo todo mới"""
    return todo_service.create_todo(todo, db)


@router.get("", status_code=200)
def get_todos(
    db: Session = Depends(get_db),
    is_done: Optional[bool] = None,
    q: Optional[str] = None,
    sort: str = "created_at",
    limit: int = Query(10, gt=0),
    offset: int = Query(0, ge=0)
):
    """Lấy danh sách todos"""
    return todo_service.get_todos(
        db=db,
        is_done=is_done,
        q=q,
        sort=sort,
        limit=limit,
        offset=offset
    )


@router.get("/{todo_id}", status_code=200, response_model=Todo)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """Lấy todo theo ID"""
    return todo_service.get_todo(todo_id, db)


@router.patch("/{todo_id}", status_code=200, response_model=Todo)
def update_todo(todo_id: int, updated_todo: TodoUpdate, db: Session = Depends(get_db)):
    """Cập nhật một phần todo"""
    return todo_service.update_todo(todo_id, updated_todo, db)


@router.post("/{todo_id}/complete", status_code=200, response_model=Todo)
def complete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Đánh dấu todo là hoàn thành"""
    return todo_service.complete_todo(todo_id, db)


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Xóa todo"""
    todo_service.delete_todo(todo_id, db)
