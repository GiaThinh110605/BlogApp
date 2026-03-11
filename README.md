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