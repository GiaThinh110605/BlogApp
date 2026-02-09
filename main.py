from fastapi import FastAPI, HTTPException
from typing import Optional
from fastapi.params import Query
from pydantic import BaseModel, Field
from datetime import datetime
from pydantic import validator

app = FastAPI()

# cap 0

@app.get("/")
def read_root():
    return {"Chào mừng bạn đến với ứng dụng FastAPI!"}

@app.get("/health")
def read_health():
    return {"status": "ok"}

# cap 1
class Todo(BaseModel):
    id: int
    title: str
    is_done: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('title')
    def title_length(cls, v):
        if not v or len(v) < 3 or len(v) > 100:
            raise ValueError('Title must be 3-100 characters')
        return v

todo_db = []

@app.post("/todos", status_code=201)
def create_todo(todo: Todo):
    if any(t.id == todo.id for t in todo_db):
        raise HTTPException(status_code=400, detail="Id đã tồn tại")
    todo_db.append(todo)
    return todo

@app.get("/todos", status_code=200)
def get_todos(
    is_done: Optional[bool] = None,
    q: Optional[str] = None,
    sort: str = "created_at",
    limit: int = Query(10, gt=0),
    offset: int = Query(0, ge=0)
):
    filtered = todo_db
    if is_done is not None:
        filtered = [todo for todo in filtered if todo.is_done == is_done]

    if q:
        q_lower = q.lower()
        filtered = [todo for todo in filtered if q_lower in todo.title.lower()]

    total = len(filtered)

    if sort == "created_at":
        filtered.sort(key=lambda x: x.created_at)
    elif sort == "-created_at":
        filtered.sort(key=lambda x: x.created_at, reverse=True)
    else:
        raise HTTPException(status_code=400, detail="Tham số sắp xếp không hợp lệ")
    
    paginated_todos = filtered[offset: offset + limit]
    
    return {
        "items": paginated_todos,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/todos/{todo_id}", status_code=200)
def get_todo(todo_id: int):
    for todo in todo_db:
        if todo.id == todo_id:
            return todo
    raise HTTPException (status_code=404, detail="Todo này không tồn tại")

@app.put("/todos/{todo_id}", status_code=200)
def update_todo(todo_id: int, updated_todo: Todo):
    for index, todo in enumerate(todo_db):
        if todo.id == todo_id:
            todo_db[index] = updated_todo
            return updated_todo
    raise HTTPException(status_code=404, detail="Todo này không tồn tại")

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    for index, todo in enumerate(todo_db):
        if todo.id == todo_id:
            del todo_db[index]
            return
    raise HTTPException(status_code=404, detail="Todo này không tồn tại")