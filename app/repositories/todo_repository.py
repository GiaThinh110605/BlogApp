from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_
from datetime import datetime, date
from app.schemas.todo import TodoCreate, TodoUpdate
from app.models.todo import Todo as TodoModel, Tag


class TodoRepository:
    """Tầng repository: Quản lý truy cập dữ liệu"""
    
    @staticmethod
    def create(todo: TodoCreate, db: Session, owner_id: int) -> TodoModel:
        """Tạo todo mới"""
        db_todo = TodoModel(**todo.dict(exclude={"tag_ids"}), owner_id=owner_id)
        
        # Add tags
        if todo.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(todo.tag_ids)).all()
            db_todo.tags = tags
        
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
    
    @staticmethod
    def get_by_id(todo_id: int, db: Session, owner_id: int) -> Optional[TodoModel]:
        """Lấy todo theo ID của user"""
        return db.query(TodoModel).filter(
            TodoModel.id == todo_id,
            TodoModel.owner_id == owner_id
        ).first()
    
    @staticmethod
    def get_user_todos(user_id: int, db: Session, skip: int = 0, limit: int = 100) -> List[TodoModel]:
        return db.query(TodoModel).filter(TodoModel.owner_id == user_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_overdue_todos(user_id: int, db: Session) -> List[TodoModel]:
        now = datetime.utcnow()
        return db.query(TodoModel).filter(
            and_(
                TodoModel.owner_id == user_id,
                TodoModel.due_date < now,
                TodoModel.is_done == False
            )
        ).all()
    
    @staticmethod
    def get_today_todos(user_id: int, db: Session) -> List[TodoModel]:
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        return db.query(TodoModel).filter(
            and_(
                TodoModel.owner_id == user_id,
                TodoModel.due_date >= start_of_day,
                TodoModel.due_date <= end_of_day
            )
        ).all()
    
    @staticmethod
    def get_all(
        db: Session,
        owner_id: int,
        is_done: Optional[bool] = None,
        search: Optional[str] = None,
        sort: str = "created_at",
        limit: int = 10,
        offset: int = 0
    ) -> tuple[List[TodoModel], int]:
        """Lấy tất cả todos của user với filter, search, sort, pagination từ database"""
        query = db.query(TodoModel).filter(TodoModel.owner_id == owner_id)

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
    def update(todo_id: int, updated_data: TodoUpdate, db: Session, owner_id: int) -> Optional[TodoModel]:
        """Cập nhật todo của user"""
        todo = db.query(TodoModel).filter(
            TodoModel.id == todo_id,
            TodoModel.owner_id == owner_id
        ).first()
        if todo:
            update_data = updated_data.dict(exclude_unset=True)
            
            # Handle tags separately
            tag_ids = update_data.pop("tag_ids", None)
            
            for field, value in update_data.items():
                setattr(todo, field, value)
            
            # Update tags if provided
            if tag_ids is not None:
                tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
                todo.tags = tags
            
            db.commit()
            db.refresh(todo)
        return todo
    
    @staticmethod
    def delete(todo_id: int, db: Session, owner_id: int) -> bool:
        """Xóa todo của user"""
        todo = db.query(TodoModel).filter(
            TodoModel.id == todo_id,
            TodoModel.owner_id == owner_id
        ).first()
        if todo:
            db.delete(todo)
            db.commit()
            return True
        return False
    
    @staticmethod
    def exists(todo_id: int, db: Session, owner_id: int) -> bool:
        """Kiểm tra todo của user có tồn tại không"""
        return db.query(TodoModel).filter(
            TodoModel.id == todo_id,
            TodoModel.owner_id == owner_id
        ).first() is not None
    
    @staticmethod
    def complete(todo_id: int, db: Session, owner_id: int) -> Optional[TodoModel]:
        """Đánh dấu todo của user là hoàn thành"""
        todo = db.query(TodoModel).filter(
            TodoModel.id == todo_id,
            TodoModel.owner_id == owner_id
        ).first()
        if todo:
            todo.is_done = True
            db.commit()
            db.refresh(todo)
        return todo
