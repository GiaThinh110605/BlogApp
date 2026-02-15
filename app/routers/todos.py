from fastapi import APIRouter, Query
from typing import Optional
from schemas.todo import TodoCreate, TodoUpdate, Todo
from services.todo_service import TodoService


router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}},
)

# Initialize service
todo_service = TodoService()


@router.post("", status_code=201, response_model=Todo)
def create_todo(todo: TodoCreate):
    """Tạo todo mới"""
    return todo_service.create_todo(todo)


@router.get("", status_code=200)
def get_todos(
    is_done: Optional[bool] = None,
    q: Optional[str] = None,
    sort: str = "created_at",
    limit: int = Query(10, gt=0),
    offset: int = Query(0, ge=0)
):
    """Lấy danh sách todos"""
    return todo_service.get_todos(
        is_done=is_done,
        q=q,
        sort=sort,
        limit=limit,
        offset=offset
    )


@router.get("/{todo_id}", status_code=200, response_model=Todo)
def get_todo(todo_id: int):
    """Lấy todo theo ID"""
    return todo_service.get_todo(todo_id)


@router.put("/{todo_id}", status_code=200, response_model=Todo)
def update_todo(todo_id: int, updated_todo: TodoUpdate):
    """Cập nhật todo"""
    return todo_service.update_todo(todo_id, updated_todo)


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    """Xóa todo"""
    todo_service.delete_todo(todo_id)
