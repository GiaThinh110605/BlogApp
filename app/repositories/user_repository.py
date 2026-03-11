from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.models.user import User as UserModel
from app.core.auth import get_password_hash
from app.core.auth import verify_password



class UserRepository:
    """Tầng repository cho User"""
    
    @staticmethod
    def create(user: UserCreate, db: Session) -> UserModel:
        """Tạo user mới"""
        
        hashed_password = get_password_hash(user.password)
        db_user = UserModel(
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_by_email(email: str, db: Session) -> Optional[UserModel]:
        """Lấy user theo email"""
        return db.query(UserModel).filter(UserModel.email == email).first()
    
    @staticmethod
    def get_by_id(user_id: int, db: Session) -> Optional[UserModel]:
        """Lấy user theo ID"""
        return db.query(UserModel).filter(UserModel.id == user_id).first()
    
    @staticmethod
    def authenticate(email: str, password: str, db: Session) -> Optional[UserModel]:
        """Xác thực user"""
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
            
        return user
    
    @staticmethod
    def exists(email: str, db: Session) -> bool:
        """Kiểm tra email đã tồn tại chưa"""
        return db.query(UserModel).filter(UserModel.email == email).first() is not None
