- Cấp 0: Làm quen với fast api 
- cài uvicorn: pip install fastapi uvicorn
- chạy backend: python3 -m uvicorn main:app --reload

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