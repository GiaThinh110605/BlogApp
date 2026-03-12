- Cấp 0: Làm quen với fast api 
- cài uvicorn: pip install fastapi uvicorn
- chạy backend: python3 -m uvicorn main:app --reload
- localhost:8000/docs để truy cập api

- Cấp 1: Học cách tạo sche, và viết các endpoint

- Cấp 2: Học cách validation, phân trang, sử dụng thunder client trong vscode để test api 

- Cấp 3: 
+ Cấu trúc thư mục:
    - app/
        - core/ # cấu hình của hệ thống(config.py, ...)
        - schemas/ # Pydantic models (Request, Response body)
        - repositories/ # Giao tiếp với database
        - services/ # Xử lý nghiệp vụ
        - routers/ # Định nghĩa các endpoin
        - main.py # khởi tạo ứng dụng 
    .env # file cấu hình môi trường

- Cấp 4: Dùng database(SQLite, PostgreSQL) + ORM(SQLAlchemy)

- 1. Cài đặt thư viện: pip3 install fastapi uvicorn sqlalchemy alembic psycopg2-binary
- 2. cấu hình database:    database_url: str = "sqlite:///./blog_app.db"
    - sqlite:// : đường dẫn báo cho biết là đang dùng sqlite
    - blog_app.db: tệp db được tạo ra 
- 3. Tạo session để kết nối database
    - Cần tạo session để kết nối với engine(database)
    - Mọi model đều kết nối thông qua Base class

- 4. Tạo SQLAIchemy Model 

- 5. cập nhật schema đang có thêm des

- 6. khởi tạo cho migration: alembic init alembic

- 7. chỉnh sửa alembic.ini 
    - sqlalchemy.url = sqlite:///./blog_app.db

- 8. cấu hình Alembic import models 
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.core.database import Base
from app.models import todo  # Import tất cả models
target_metadata = Base.metadata

- 9. tạo migration: alembic revision --autogenerate -m "create todos table"

- 10. 
Cài sqlite: pip install psycopg2-binary

- migration alembic: 
    - alembic init alembic
    - alembic revision --autogenerate -m "create todos table"
    - alembic upgrade head

Sử dụng ORM
python 

# import những thứ cần thiết
from app.core.database import SessionLocal, engine
from app.models.todo import Todo

# Kiểm tra engine
print("Database URL:", engine.url)
print("Database connected:", engine.dialect.name)

# Khi chạy không được
- kiểm tra table được tạo trong main.py, database.py
- kiểm tra mình đang trỏ đúng thư nếu báo module không tìm thấy
# 5. 

## Cấp 5: Authentication + User riêng

### Mục tiêu:
- Implement user authentication với JWT
- Mỗi user chỉ có thể truy cập todos của riêng mình
- Password hashing với bcrypt
- User registration, login, và profile endpoints

### 1. Cài đặt thư viện:
```bash
pip3 install fastapi uvicorn sqlalchemy alembic psycopg2-binary python-jose passlib bcrypt python-multipart
```

### 2. Tạo User Model:
```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### 3. Cập nhật Todo Model:
```python
# app/models/todo.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Todo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign key đến User
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship
    owner = relationship("User", back_populates="todos")
```

### 4. Tạo User Schemas:
```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
```

### 5. Authentication Utilities:
```python
# app/core/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise ValueError("Invalid token")
        return email
    except JWTError:
        raise ValueError("Invalid token")
```

### 6. Security Dependency:
```python
# app/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import verify_token
from app.repositories.user_repository import UserRepository
from app.models.user import User

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    email = verify_token(token)
    
    user_repo = UserRepository()
    user = user_repo.get_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user
```

### 7. User Repository:
```python
# app/repositories/user_repository.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.auth import get_password_hash

class UserRepository:
    def create(self, user: UserCreate, db: Session) -> User:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def get_by_email(self, email: str, db: Session) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    def authenticate(self, email: str, password: str, db: Session) -> Optional[User]:
        user = self.get_by_email(email, db)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def exists(self, email: str, db: Session) -> bool:
        return db.query(User).filter(User.email == email).first() is not None
```

### 8. User Service:
```python
# app/services/user_service.py
from datetime import timedelta
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, User, Token
from app.repositories.user_repository import UserRepository
from app.core.auth import create_access_token, verify_password
from app.core.config import settings

class UserService:
    def __init__(self):
        self.repo = UserRepository()
    
    def register(self, user: UserCreate, db: Session) -> User:
        if self.repo.exists(user.email, db):
            raise ValueError("Email already registered")
        return self.repo.create(user, db)
    
    def login(self, user_login: UserLogin, db: Session) -> Token:
        user = self.repo.authenticate(user_login.email, user_login.password, db)
        if not user:
            raise ValueError("Invalid email or password")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
    
    def get_current_user(self, email: str, db: Session) -> User:
        user = self.repo.get_by_email(email, db)
        if not user:
            raise ValueError("User not found")
        return user
```

### 9. Auth Router:
```python
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, User, Token
from app.services.user_service import UserService
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        user_service = UserService()
        return user_service.register(user, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        user_service = UserService()
        return user_service.login(user, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
```

### 10. Cập nhật Todo Router với Authentication:
```python
# app/routers/todos.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.services.todo_service import TodoService
from app.models.user import User

router = APIRouter(prefix="/todos", tags=["todos"])

@router.post("/", response_model=TodoResponse)
def create_todo(
    todo: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo_service = TodoService()
    return todo_service.create_todo(todo, current_user.id, db)

@router.get("/", response_model=list[TodoResponse])
def get_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    todo_service = TodoService()
    return todo_service.get_todos(current_user.id, db, skip=skip, limit=limit)
```

### 11. Database Migration:
cách 1: thay đổi model trước khi migrate
```bash
# Tạo migration cho users table
alembic revision --autogenerate -m "create users and todos tables"

# Chạy migration
alembic upgrade head
```
- Cách 2: drop db rồi migration
- delete database: rm blog_app.db
- reset history: alembic stamp base
- generate migration: alembic revision --autogenerate -m "create all tables"
- run migration: alembic upgrade head



### 12. Cập nhật Config:
```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI Todo Application"
    debug: bool = True
    api_v1_str: str = "/api/v1"
    secret_key: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    database_url: str = "sqlite:///./blog_app.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### 13. Cập nhật .env:
```bash
# .env
app_name="FastAPI Todo Application"
debug=true
api_v1_str="/api/v1"
database_url="sqlite:///./blog_app.db"
```

### 14. Cách chạy ứng dụng:

#### Bước 1: Kích hoạt virtual environment
```bash
source .venv/bin/activate
```

#### Bước 2: Clear biến môi trường cũ (nếu có)
```bash
unset DATABASE_URL
```

#### Bước 3: Chạy server
```bash
python3 -m uvicorn app.main:app --reload --port 8000
```

#### Bước 4: Test API

**Đăng ký user:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "user@example.com",
  "password": "password123"
}'
```

**Đăng nhập:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "user@example.com",
  "password": "password123"
}'
```

**Tạo todo (cần token):**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/todos' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -d '{
  "title": "Todo của tôi",
  "description": "Mô tả todo"
}'
```

### 15. Swagger UI với Authentication:
1. Truy cập: `http://localhost:8000/docs`
2. Click nút "Authorize" (ổ khóa 🔒)
3. Nhập token: `Bearer YOUR_TOKEN_HERE`
4. Click "Authorize"
5. Test các endpoints

### 16. Lỗi thường gặp và cách fix:

#### Lỗi 1: "Could not import module 'main'"
```bash
# Dùng đúng module path
python3 -m uvicorn app.main:app --reload --port 8000
```

#### Lỗi 2: "database does not exist" (PostgreSQL)
```bash
# Clear biến môi trường
unset DATABASE_URL
# Restart server
```

#### Lỗi 3: "password cannot be longer than 72 bytes"
```bash
# Downgrade bcrypt
pip install "bcrypt<4.0.0"
# Restart server
```

#### Lỗi 4: "Not authenticated"
```bash
# Cần thêm header Authorization
-H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 17. Kiểm tra database:
```python
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.models.todo import Todo

print("Database URL:", engine.url)
print("Database connected:", engine.dialect.name)

# Kiểm tra data
db = SessionLocal()
users = db.query(User).all()
todos = db.query(Todo).all()
print(f"Users: {len(users)}")
print(f"Todos: {len(todos)}")
db.close()
```

### 18. Tóm tắt features Cấp 5:
✅ User registration & login  
✅ JWT token authentication  
✅ Password hashing với bcrypt  
✅ User-specific todos (authorization)  
✅ Protected endpoints  
✅ Swagger UI với auth  
✅ SQLite database  
✅ Error handling  
✅ Input validation 

## Cấp 6 — Nâng cao (tag, deadline, nhắc việc)

### Mục tiêu:
Thêm tính năng giống app thật với due_date, tags, notifications

### 1. Cập nhật Todo Model:
```python
# app/models/todo.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Todo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text(), nullable=True)
    is_done = Column(Boolean, default=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="todos")
    
    # Many-to-many relationship with tags
    tags = relationship("Tag", secondary="todo_tags", back_populates="todos")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default="#000000")  # Hex color
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    todos = relationship("Todo", secondary="todo_tags", back_populates="tags")

class TodoTag(Base):
    __tablename__ = "todo_tags"
    
    todo_id = Column(Integer, ForeignKey("todos.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
```

### 2. Cập nhật Todo Schemas:
```python
# app/schemas/todo.py
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List, Optional

class TagBase(BaseModel):
    name: str
    color: str = "#000000"

class Tag(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_done: bool = False

class TodoCreate(TodoBase):
    tag_ids: Optional[List[int]] = []

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_done: Optional[bool] = None
    tag_ids: Optional[List[int]] = None

class TodoResponse(TodoBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    tags: List[Tag] = []
    
    class Config:
        from_attributes = True

class TodoSummary(BaseModel):
    id: int
    title: str
    due_date: Optional[datetime]
    is_done: bool
    tags: List[str] = []
```

### 3. Tag Repository:
```python
# app/repositories/tag_repository.py
from sqlalchemy.orm import Session
from app.models.tag import Tag
from app.schemas.todo import TagBase

class TagRepository:
    def create(self, tag: TagBase, db: Session) -> Tag:
        db_tag = Tag(**tag.dict())
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag
    
    def get_all(self, db: Session) -> List[Tag]:
        return db.query(Tag).all()
    
    def get_by_id(self, tag_id: int, db: Session) -> Optional[Tag]:
        return db.query(Tag).filter(Tag.id == tag_id).first()
    
    def get_by_name(self, name: str, db: Session) -> Optional[Tag]:
        return db.query(Tag).filter(Tag.name == name).first()
    
    def get_or_create(self, tag_name: str, db: Session) -> Tag:
        tag = self.get_by_name(tag_name, db)
        if not tag:
            tag = self.create(TagBase(name=tag_name), db)
        return tag
```

### 4. Cập nhật Todo Repository:
```python
# app/repositories/todo_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date
from app.models.todo import Todo, Tag
from app.schemas.todo import TodoCreate, TodoUpdate

class TodoRepository:
    def create(self, todo: TodoCreate, owner_id: int, db: Session) -> Todo:
        db_todo = Todo(**todo.dict(exclude={"tag_ids"}), owner_id=owner_id)
        
        # Add tags
        if todo.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(todo.tag_ids)).all()
            db_todo.tags = tags
        
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
    
    def get_user_todos(self, user_id: int, db: Session, skip: int = 0, limit: int = 100) -> List[Todo]:
        return db.query(Todo).filter(Todo.owner_id == user_id).offset(skip).limit(limit).all()
    
    def get_overdue_todos(self, user_id: int, db: Session) -> List[Todo]:
        now = datetime.utcnow()
        return db.query(Todo).filter(
            and_(
                Todo.owner_id == user_id,
                Todo.due_date < now,
                Todo.is_done == False
            )
        ).all()
    
    def get_today_todos(self, user_id: int, db: Session) -> List[Todo]:
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        return db.query(Todo).filter(
            and_(
                Todo.owner_id == user_id,
                Todo.due_date >= start_of_day,
                Todo.due_date <= end_of_day
            )
        ).all()
    
    def get_by_id(self, todo_id: int, user_id: int, db: Session) -> Optional[Todo]:
        return db.query(Todo).filter(
            and_(Todo.id == todo_id, Todo.owner_id == user_id)
        ).first()
    
    def update(self, todo_id: int, todo_update: TodoUpdate, user_id: int, db: Session) -> Optional[Todo]:
        db_todo = self.get_by_id(todo_id, user_id, db)
        if not db_todo:
            return None
        
        update_data = todo_update.dict(exclude_unset=True)
        
        # Handle tags separately
        tag_ids = update_data.pop("tag_ids", None)
        
        for field, value in update_data.items():
            setattr(db_todo, field, value)
        
        # Update tags if provided
        if tag_ids is not None:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            db_todo.tags = tags
        
        db.commit()
        db.refresh(db_todo)
        return db_todo
    
    def delete(self, todo_id: int, user_id: int, db: Session) -> bool:
        db_todo = self.get_by_id(todo_id, user_id, db)
        if not db_todo:
            return False
        
        db.delete(db_todo)
        db.commit()
        return True
```

### 5. Cập nhật Todo Service:
```python
# app/services/todo_service.py
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.repositories.todo_repository import TodoRepository
from app.repositories.tag_repository import TagRepository

class TodoService:
    def __init__(self):
        self.repo = TodoRepository()
        self.tag_repo = TagRepository()
    
    def create_todo(self, todo: TodoCreate, user_id: int, db: Session) -> TodoResponse:
        db_todo = self.repo.create(todo, user_id, db)
        return TodoResponse.from_orm(db_todo)
    
    def get_todos(self, user_id: int, db: Session, skip: int = 0, limit: int = 100) -> List[TodoResponse]:
        todos = self.repo.get_user_todos(user_id, db, skip, limit)
        return [TodoResponse.from_orm(todo) for todo in todos]
    
    def get_overdue_todos(self, user_id: int, db: Session) -> List[TodoResponse]:
        todos = self.repo.get_overdue_todos(user_id, db)
        return [TodoResponse.from_orm(todo) for todo in todos]
    
    def get_today_todos(self, user_id: int, db: Session) -> List[TodoResponse]:
        todos = self.repo.get_today_todos(user_id, db)
        return [TodoResponse.from_orm(todo) for todo in todos]
    
    def get_todo_by_id(self, todo_id: int, user_id: int, db: Session) -> Optional[TodoResponse]:
        todo = self.repo.get_by_id(todo_id, user_id, db)
        return TodoResponse.from_orm(todo) if todo else None
    
    def update_todo(self, todo_id: int, todo_update: TodoUpdate, user_id: int, db: Session) -> Optional[TodoResponse]:
        todo = self.repo.update(todo_id, todo_update, user_id, db)
        return TodoResponse.from_orm(todo) if todo else None
    
    def delete_todo(self, todo_id: int, user_id: int, db: Session) -> bool:
        return self.repo.delete(todo_id, user_id, db)
```

### 6. Cập nhật Todo Router:
```python
# app/routers/todos.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse, TodoSummary
from app.services.todo_service import TodoService
from app.models.user import User

router = APIRouter(prefix="/todos", tags=["todos"])

@router.post("/", response_model=TodoResponse)
def create_todo(
    todo: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo_service = TodoService()
    return todo_service.create_todo(todo, current_user.id, db)

@router.get("/", response_model=list[TodoResponse])
def get_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    todo_service = TodoService()
    return todo_service.get_todos(current_user.id, db, skip=skip, limit=limit)

@router.get("/overdue", response_model=list[TodoResponse])
def get_overdue_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo_service = TodoService()
    return todo_service.get_overdue_todos(current_user.id, db)

@router.get("/today", response_model=list[TodoResponse])
def get_today_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo_service = TodoService()
    return todo_service.get_today_todos(current_user.id, db)

@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo_service = TodoService()
    todo = todo_service.get_todo_by_id(todo_id, current_user.id, db)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo_service = TodoService()
    todo = todo_service.update_todo(todo_id, todo_update, current_user.id, db)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.delete("/{todo_id}")
def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo_service = TodoService()
    if not todo_service.delete_todo(todo_id, current_user.id, db):
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}
```

### 7. Tag Router:
```python
# app/routers/tags.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.todo import TagBase, Tag
from app.repositories.tag_repository import TagRepository
from app.models.user import User

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("/", response_model=Tag)
def create_tag(
    tag: TagBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tag_repo = TagRepository()
    # Check if tag already exists
    existing = tag_repo.get_by_name(tag.name, db)
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")
    
    return tag_repo.create(tag, db)

@router.get("/", response_model=list[Tag])
def get_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tag_repo = TagRepository()
    return tag_repo.get_all(db)
```

### 8. Database Migration:
```bash
# Generate migration cho tags và todo_tags
alembic revision --autogenerate -m "add tags and due_date to todos"

# Chạy migration
alembic upgrade head
```

### 9. Cập nhật main.py:
```python
# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.routers.todos import router as todos_router
from app.routers.auth import router as auth_router
from app.routers.tags import router as tags_router

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0"
)

app.include_router(auth_router, prefix=settings.api_v1_str)
app.include_router(todos_router, prefix=settings.api_v1_str)
app.include_router(tags_router, prefix=settings.api_v1_str)
```

### 10. Test API Examples:

**Tạo todo với due_date và tags:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/todos' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer TOKEN' \
  -d '{
  "title": "Hoàn thành báo cáo",
  "description": "Báo cáo quarterly",
  "due_date": "2026-03-15T17:00:00Z",
  "tag_ids": [1, 2]
}'
```

**Lấy danh sách quá hạn:**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/todos/overdue' \
  -H 'Authorization: Bearer TOKEN'
```

**Lấy việc cần làm hôm nay:**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/todos/today' \
  -H 'Authorization: Bearer TOKEN'
```

### 11. Features Cấp 6:
✅ Due date cho todos  
✅ Tag system (many-to-many)  
✅ Overdue todos endpoint  
✅ Today todos endpoint  
✅ Tag management  
✅ Color coding cho tags  
✅ Advanced filtering 

## Cấp 7 — Testing + tài liệu + deploy

### Mục tiêu:
Hoàn chỉnh quy trình development với testing và documentation

### 1. Cài đặt test dependencies:
```bash
pip install pytest pytest-asyncio httpx
```

### 2. Cấu hình test database:
```python
# conftest.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Test database URL (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(setup_database):
    return TestClient(app)

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def auth_headers(client, test_user):
    # Register user
    client.post("/api/v1/auth/register", json=test_user)
    
    # Login to get token
    response = client.post("/api/v1/auth/login", json=test_user)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
```

### 3. Test Authentication:
```python
# test_auth.py
import pytest
from fastapi import status

def test_register_user(client):
    """Test tạo user thành công"""
    user_data = {
        "email": "newuser@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data

def test_register_duplicate_email(client, test_user):
    """Test register email đã tồn tại"""
    # Register lần đầu
    client.post("/api/v1/auth/register", json=test_user)
    
    # Register lần 2 - nên fail
    response = client.post("/api/v1/auth/register", json=test_user)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()

def test_login_success(client, test_user):
    """Test đăng nhập thành công"""
    # Register user trước
    client.post("/api/v1/auth/register", json=test_user)
    
    # Login
    response = client.post("/api/v1/auth/login", json=test_user)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test đăng nhập sai thông tin"""
    wrong_user = {
        "email": "wrong@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=wrong_user)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in response.json()["detail"].lower()

def test_get_current_user(client, auth_headers):
    """Test lấy thông tin user hiện tại"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "id" in data

def test_get_current_user_unauthorized(client):
    """Test lấy thông tin user mà không có token"""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

### 4. Test Todos:
```python
# test_todos.py
import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_create_todo_success(client, auth_headers):
    """Test tạo todo thành công"""
    todo_data = {
        "title": "Test Todo",
        "description": "Test Description",
        "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        "tag_ids": []
    }
    response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == todo_data["title"]
    assert data["description"] == todo_data["description"]
    assert "id" in data
    assert "owner_id" in data

def test_create_todo_validation_fail(client, auth_headers):
    """Test tạo todo với validation fail"""
    # Title quá ngắn
    todo_data = {
        "title": "ab",  # < 3 ký tự
        "description": "Test Description"
    }
    response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_todos_success(client, auth_headers):
    """Test lấy danh sách todos thành công"""
    # Tạo todo trước
    todo_data = {
        "title": "Test Todo",
        "description": "Test Description"
    }
    client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    
    # Lấy danh sách
    response = client.get("/api/v1/todos", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0

def test_get_todo_success(client, auth_headers):
    """Test lấy todo cụ thể thành công"""
    # Tạo todo trước
    todo_data = {
        "title": "Test Todo",
        "description": "Test Description"
    }
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    # Lấy todo cụ thể
    response = client.get(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == todo_data["title"]

def test_get_todo_not_found(client, auth_headers):
    """Test lấy todo không tồn tại"""
    response = client.get("/api/v1/todos/99999", headers=auth_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()

def test_get_todo_unauthorized(client):
    """Test lấy todo mà không có token"""
    response = client.get("/api/v1/todos/1")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_todo_success(client, auth_headers):
    """Test cập nhật todo thành công"""
    # Tạo todo trước
    todo_data = {
        "title": "Original Title",
        "description": "Original Description"
    }
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    # Cập nhật
    update_data = {
        "title": "Updated Title",
        "is_done": True
    }
    response = client.patch(f"/api/v1/todos/{todo_id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["is_done"] == True

def test_delete_todo_success(client, auth_headers):
    """Test xóa todo thành công"""
    # Tạo todo trước
    todo_data = {
        "title": "Todo to Delete",
        "description": "Will be deleted"
    }
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    # Xóa
    response = client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Kiểm tra không còn tồn tại
    get_response = client.get(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_get_overdue_todos(client, auth_headers):
    """Test lấy todos quá hạn"""
    # Tạo overdue todo
    overdue_todo = {
        "title": "Overdue Todo",
        "description": "Should be overdue",
        "due_date": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    }
    client.post("/api/v1/todos", json=overdue_todo, headers=auth_headers)
    
    # Lấy overdue todos
    response = client.get("/api/v1/todos/overdue", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Kiểm tra có overdue todo
    assert len(data) > 0
    assert data[0]["is_done"] == False

def test_get_today_todos(client, auth_headers):
    """Test lấy todos hôm nay"""
    # Tạo today todo
    today_todo = {
        "title": "Today Todo",
        "description": "Should be today",
        "due_date": datetime.utcnow().isoformat() + "Z"
    }
    client.post("/api/v1/todos", json=today_todo, headers=auth_headers)
    
    # Lấy today todos
    response = client.get("/api/v1/todos/today", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
```

### 5. Test Tags:
```python
# test_tags.py
import pytest
from fastapi import status

def test_create_tag_success(client, auth_headers):
    """Test tạo tag thành công"""
    tag_data = {
        "name": "work",
        "color": "#FF0000"
    }
    response = client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == tag_data["name"]
    assert data["color"] == tag_data["color"]
    assert "id" in data

def test_create_duplicate_tag(client, auth_headers):
    """Test tạo tag trùng tên"""
    tag_data = {
        "name": "duplicate",
        "color": "#00FF00"
    }
    
    # Tạo lần đầu
    client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
    
    # Tạo lần 2 - nên fail
    response = client.post("/api/v1/tags", json=tag_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()

def test_get_tags_success(client, auth_headers):
    """Test lấy danh sách tags"""
    # Tạo vài tags
    tags = [
        {"name": "work", "color": "#FF0000"},
        {"name": "personal", "color": "#00FF00"}
    ]
    for tag in tags:
        client.post("/api/v1/tags", json=tag, headers=auth_headers)
    
    # Lấy danh sách
    response = client.get("/api/v1/tags", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
```

### 6. Chạy tests:
```bash
# Chạy tất cả tests
pytest

# Chạy với coverage
pytest --cov=app --cov-report=html

# Chạy test cụ thể
pytest test_auth.py -v

# Chạy test với marker
pytest -m "not slow"
```

### 7. Test Configuration (pyproject.toml):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests"
]
```

### 8. GitHub Actions CI/CD:
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio httpx pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 9. Production Requirements:
```txt
# requirements-prod.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0
```

### 10. Environment Variables cho Production:
```bash
# .env.production
APP_NAME="FastAPI Todo App"
DEBUG=false
SECRET_KEY="your-production-secret-key"
DATABASE_URL="sqlite:///./production.db"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 11. Cấu hình Production:
```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI Todo Application"
    debug: bool = False
    api_v1_str: str = "/api/v1"
    secret_key: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    database_url: str = "sqlite:///./blog_app.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Load environment-specific config
import os
if os.getenv("ENVIRONMENT") == "production":
    from dotenv import load_dotenv
    load_dotenv(".env.production")

settings = Settings()
```

### 12. Cập nhật requirements.txt:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
pytest-cov==4.1.0
```

### 13. Scripts cho development:
```bash
#!/bin/bash
# scripts/run_tests.sh
echo "Running tests..."
pytest --cov=app --cov-report=html

echo "Starting development server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 14. Features Cấp 7:
✅ Pytest testing framework  
✅ Test coverage  
✅ Authentication tests  
✅ CRUD operation tests  
✅ Validation tests  
✅ Error handling tests  
✅ GitHub Actions CI/CD  
✅ Production configuration  
✅ Environment management  
✅ Documentation complete 

## Cấp 8 — Soft Delete & nâng cao

### Mục tiêu:
Thêm soft delete và các tính năng nâng cao khác

### 1. Soft Delete Implementation:
```python
# app/models/base.py
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base

class SoftDeleteMixin:
    """Mixin cho soft delete functionality"""
    
    @declared_attr
    def deleted_at(cls):
        return Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self):
        """Thực hiện soft delete"""
        self.deleted_at = func.now()
    
    def restore(self):
        """Khôi phục từ soft delete"""
        self.deleted_at = None
    
    @property
    def is_deleted(self):
        """Kiểm tra đã bị xóa chưa"""
        return self.deleted_at is not None
```

### 2. Cập nhật Todo Model:
```python
# app/models/todo.py
from app.models.base import SoftDeleteMixin

class Todo(Base, SoftDeleteMixin):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_done = Column(Boolean, default=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    owner = relationship("User", back_populates="todos")
    tags = relationship("Tag", secondary="todo_tags", back_populates="todos")
```

### 3. Soft Delete Repository:
```python
# app/repositories/soft_delete_repository.py
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
```

### 4. Soft Delete Service:
```python
# app/services/soft_delete_service.py
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.soft_delete_repository import SoftDeleteRepository
from app.models.todo import Todo

class SoftDeleteService:
    def __init__(self):
        self.repo = SoftDeleteRepository()
    
    def get_active_todos(self, user_id: int, db: Session, skip: int = 0, limit: int = 100) -> List[Todo]:
        """Lấy todos đang hoạt động"""
        return self.repo.get_active_todos(user_id, db, skip, limit)
    
    def get_deleted_todos(self, user_id: int, db: Session, skip: int = 0, limit: int = 100) -> List[Todo]:
        """Lấy todos đã bị xóa (trash)"""
        return self.repo.get_deleted_todos(user_id, db, skip, limit)
    
    def soft_delete_todo(self, todo_id: int, user_id: int, db: Session) -> Todo:
        """Chuyển todo vào trash"""
        todo = self.repo.soft_delete_todo(todo_id, user_id, db)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo không tồn tại hoặc đã bị xóa")
        return todo
    
    def restore_todo(self, todo_id: int, user_id: int, db: Session) -> Todo:
        """Khôi phục todo từ trash"""
        todo = self.repo.restore_todo(todo_id, user_id, db)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo không tồn tại trong trash")
        return todo
    
    def permanent_delete_todo(self, todo_id: int, user_id: int, db: Session) -> None:
        """Xóa vĩnh viễn todo"""
        if not self.repo.permanent_delete_todo(todo_id, user_id, db):
            raise HTTPException(status_code=404, detail="Todo không tồn tại trong trash")
    
    def empty_trash(self, user_id: int, db: Session) -> dict:
        """Dọn trash"""
        count = self.repo.empty_trash(user_id, db)
        return {"message": f"Đã xóa vĩnh viễn {count} todo", "count": count}
```

### 5. Soft Delete Router:
```python
# app/routers/trash.py
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
```

### 6. Cập nhật Todo Router:
```python
# app/routers/todos.py (thêm soft delete)

@router.delete("/{todo_id}")
def soft_delete_todo(
    todo_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete todo (chuyển vào trash)"""
    service = SoftDeleteService()
    service.soft_delete_todo(todo_id, current_user.id, db)
    return {"message": "Đã chuyển todo vào trash"}
```

### 7. Database Migration:
```python
# alembic/versions/xxxx_add_soft_delete.py
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Add deleted_at column to todos
    op.add_column('todos', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create index for better performance
    op.create_index('ix_todos_deleted_at', 'todos', ['deleted_at'])

def downgrade() -> None:
    op.drop_index('ix_todos_deleted_at', table_name='todos')
    op.drop_column('todos', 'deleted_at')
```

### 8. Cập nhật main.py:
```python
# app/main.py
from app.routers.trash import router as trash_router

app.include_router(
    trash_router,
    prefix=settings.api_v1_str
)
```

### 9. Test Soft Delete:
```python
# test_soft_delete.py
import pytest
from fastapi import status

def test_soft_delete_todo(client, auth_headers):
    """Test soft delete todo"""
    # Tạo todo
    todo_data = {"title": "Todo to delete", "description": "Will be soft deleted"}
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    # Soft delete
    response = client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert "trash" in response.json()["message"].lower()
    
    # Kiểm tra không còn trong active todos
    get_response = client.get("/api/v1/todos", headers=auth_headers)
    todos = get_response.json()["items"]
    assert todo_id not in [todo["id"] for todo in todos]

def test_get_deleted_todos(client, auth_headers):
    """Test lấy danh sách đã xóa"""
    # Tạo và soft delete todo
    todo_data = {"title": "Deleted todo", "description": "In trash"}
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    
    # Lấy trash
    response = client.get("/api/v1/trash/todos", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    deleted_todos = response.json()
    assert todo_id in [todo["id"] for todo in deleted_todos]

def test_restore_todo(client, auth_headers):
    """Test khôi phục todo"""
    # Tạo và soft delete todo
    todo_data = {"title": "Todo to restore", "description": "Will be restored"}
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    
    # Restore
    response = client.post(f"/api/v1/trash/todos/{todo_id}/restore", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Kiểm tra todo đã quay lại active
    get_response = client.get("/api/v1/todos", headers=auth_headers)
    todos = get_response.json()["items"]
    assert todo_id in [todo["id"] for todo in todos]

def test_permanent_delete_todo(client, auth_headers):
    """Test xóa vĩnh viễn"""
    # Tạo và soft delete todo
    todo_data = {"title": "Todo to permanent delete", "description": "Will be gone forever"}
    create_response = client.post("/api/v1/todos", json=todo_data, headers=auth_headers)
    todo_id = create_response.json()["id"]
    
    client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    
    # Permanent delete
    response = client.delete(f"/api/v1/trash/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Kiểm tra không còn ở đâu cả
    trash_response = client.get("/api/v1/trash/todos", headers=auth_headers)
    deleted_todos = trash_response.json()
    assert todo_id not in [todo["id"] for todo in deleted_todos]
```

### 10. API Examples:
```bash
# Soft delete todo
curl -X 'DELETE' \
  'http://localhost:8000/api/v1/todos/1' \
  -H 'Authorization: Bearer TOKEN'

# Lấy trash
curl -X 'GET' \
  'http://localhost:8000/api/v1/trash/todos' \
  -H 'Authorization: Bearer TOKEN'

# Khôi phục todo
curl -X 'POST' \
  'http://localhost:8000/api/v1/trash/todos/1/restore' \
  -H 'Authorization: Bearer TOKEN'

# Xóa vĩnh viễn
curl -X 'DELETE' \
  'http://localhost:8000/api/v1/trash/todos/1' \
  -H 'Authorization: Bearer TOKEN'

# Dọn trash
curl -X 'DELETE' \
  'http://localhost:8000/api/v1/trash/empty' \
  -H 'Authorization: Bearer TOKEN'
```

### 11. Features Cấp 8:
✅ Soft delete với deleted_at  
✅ Trash management  
✅ Restore functionality  
✅ Permanent delete  
✅ Empty trash bulk operation  
✅ Soft delete tests  
✅ Performance optimization với indexes  
✅ Data protection against accidental loss 

- migrate data: alembic revision --autogenerate -m "add soft delete deleted_at column"
- alembic upgrade head
