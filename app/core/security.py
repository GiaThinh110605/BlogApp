from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import verify_token
from app.services.user_service import UserService

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dependency để lấy user hiện tại từ token"""
    token = credentials.credentials
    email = verify_token(token)
    
    user_service = UserService()
    user = user_service.get_current_user(email, db)
    return user
