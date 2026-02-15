from typing import Optional, List
from schemas.todo import TodoCreate, Todo


todo_db: List[Todo] = []


class TodoRepository:
    """Tầng repository: Quản lý truy cập dữ liệu"""
    
    @staticmethod
    def create(todo: TodoCreate) -> Todo:
        """Tạo todo mới"""
        new_todo = Todo(id=todo.id, title=todo.title, is_done=todo.is_done)
        todo_db.append(new_todo)
        return new_todo
    
    @staticmethod
    def get_by_id(todo_id: int) -> Optional[Todo]:
        """Lấy todo theo ID"""
        for todo in todo_db:
            if todo.id == todo_id:
                return todo
        return None
    
    @staticmethod
    def get_all(
        is_done: Optional[bool] = None,
        search: Optional[str] = None,
        sort: str = "created_at",
        limit: int = 10,
        offset: int = 0
    ) -> tuple[List[Todo], int]:
        """Lấy tất cả todos với filter, search, sort, pagination"""
        filtered = todo_db
        
        # Filter by is_done
        if is_done is not None:
            filtered = [todo for todo in filtered if todo.is_done == is_done]
        
        # Search by title
        if search:
            q_lower = search.lower()
            filtered = [todo for todo in filtered if q_lower in todo.title.lower()]
        
        total = len(filtered)
        
        # Sort
        if sort == "created_at":
            filtered.sort(key=lambda x: x.created_at)
        elif sort == "-created_at":
            filtered.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        paginated = filtered[offset: offset + limit]
        
        return paginated, total
    
    @staticmethod
    def update(todo_id: int, updated_data: Todo) -> Optional[Todo]:
        """Cập nhật todo"""
        for index, todo in enumerate(todo_db):
            if todo.id == todo_id:
                todo_db[index] = updated_data
                return updated_data
        return None
    
    @staticmethod
    def delete(todo_id: int) -> bool:
        """Xóa todo"""
        for index, todo in enumerate(todo_db):
            if todo.id == todo_id:
                del todo_db[index]
                return True
        return False
    
    @staticmethod
    def exists(todo_id: int) -> bool:
        """Kiểm tra todo có tồn tại không"""
        return any(todo.id == todo_id for todo in todo_db)
