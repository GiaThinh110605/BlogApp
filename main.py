from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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

todo_db = []

@app.post("/todos", status_code=201)
def create_todo(todo: Todo):
    if any(t.id == todo.id for t in todo_db):
        raise HTTPException(status_code=400, detail="Id đã tồn tại")
    todo_db.append(todo)
    return todo

@app.get("/todos", status_code=200)
def get_todos():
    return todo_db

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