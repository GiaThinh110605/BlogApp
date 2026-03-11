from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas.user import UserCreate, UserLogin, User, Token
from app.repositories.user_repository import UserRepository
from app.core.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

class UserService:
    """Tầng service cho User"""
    
    def __init__(self):
        self.repo = UserRepository()
    
    def register(self, user: UserCreate, db: Session) -> User:
        """Đăng ký user mới"""
        # Kiểm tra email đã tồn tại chưa
        if self.repo.exists(user.email, db):
            raise HTTPException(status_code=400, detail="Email đã tồn tại")
        
        # Tạo user mới
        db_user = self.repo.create(user, db)
        return db_user
    
    def login(self, user_credentials: UserLogin, db: Session) -> Token:
        """Đăng nhập và trả về token"""
        # Xác thực user
        user = self.repo.authenticate(user_credentials.email, user_credentials.password, db)
        if not user:
            raise HTTPException(
                status_code=401, 
                detail="Email hoặc password không đúng"
            )
        
        # Tạo access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    def get_current_user(self, email: str, db: Session) -> User:
        """Lấy user hiện tại từ email"""
        user = self.repo.get_by_email(email, db)
        if user is None:
            raise HTTPException(status_code=404, detail="User không tìm thấy")
        return user
