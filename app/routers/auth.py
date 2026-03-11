from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserCreate, UserLogin, User, Token
from app.services.user_service import UserService

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

user_service = UserService()

@router.post("/register", response_model=User, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Đăng ký user mới"""
    return user_service.register(user, db)

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Đăng nhập và nhận token"""
    return user_service.login(user_credentials, db)

@router.get("/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Lấy thông tin user hiện tại"""
    return current_user
