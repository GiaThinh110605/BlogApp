from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.schemas.todo import TodoCreate, TodoUpdate
from app.models.todo import Todo as TodoModel


class TodoRepository:
    """Tầng repository: Quản lý truy cập dữ liệu"""
    
    @staticmethod
    def create(todo: TodoCreate, db: Session) -> TodoModel:
        """Tạo todo mới"""
        new_todo = TodoModel(
            title=todo.title,
            description=todo.description,
            is_done=todo.is_done
        )
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        return new_todo
    
    @staticmethod
    def get_by_id(todo_id: int, db: Session) -> Optional[TodoModel]:
        """Lấy todo theo ID"""
        return db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    
    @staticmethod
    def get_all(
        db: Session,
        is_done: Optional[bool] = None,
        search: Optional[str] = None,
        sort: str = "created_at",
        limit: int = 10,
        offset: int = 0
    ) -> tuple[List[TodoModel], int]:
        """Lấy tất cả todos với filter, search, sort, pagination từ database"""
        query = db.query(TodoModel)
        
        # Filter by is_done
        if is_done is not None:
            query = query.filter(TodoModel.is_done == is_done)
        
        # Search by title
        if search:
            query = query.filter(TodoModel.title.contains(search))
        
        # Get total count before pagination
        total = query.count()
        
        # Sort
        if sort == "-created_at":
            query = query.order_by(desc(TodoModel.created_at))
        else:
            query = query.order_by(TodoModel.created_at)
        
        # Apply pagination
        todos = query.offset(offset).limit(limit).all()
        
        return todos, total
    
    @staticmethod
    def update(todo_id: int, updated_data: TodoUpdate, db: Session) -> Optional[TodoModel]:
        """Cập nhật todo"""
        todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if todo:
            for key, value in updated_data.dict(exclude_unset=True).items():
                setattr(todo, key, value)
            db.commit()
            db.refresh(todo)
        return todo
    
    @staticmethod
    def delete(todo_id: int, db: Session) -> bool:
        """Xóa todo"""
        todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if todo:
            db.delete(todo)
            db.commit()
            return True
        return False
    
    @staticmethod
    def exists(todo_id: int, db: Session) -> bool:
        """Kiểm tra todo có tồn tại không"""
        return db.query(TodoModel).filter(TodoModel.id == todo_id).first() is not None
    
    @staticmethod
    def complete(todo_id: int, db: Session) -> Optional[TodoModel]:
        """Đánh dấu todo là hoàn thành"""
        todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if todo:
            todo.is_done = True
            db.commit()
            db.refresh(todo)
        return todo
