from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    
    @validator('email')
    def email_validation(cls, v):
        if not v or '@' not in v:
            raise ValueError('Email không hợp lệ')
        return v.lower()

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_validation(cls, v):
        if not v or len(v) < 6:
            raise ValueError('Password phải có ít nhất 6 ký tự')
        return v

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
