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