from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_done: bool = False
    
    @validator('title')
    def title_length(cls, v):
        if not v or len(v) < 3 or len(v) > 100:
            raise ValueError('Title must be 3-100 characters')
        return v

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    pass

class Todo(TodoBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TodoResponse(BaseModel):
    items: list[Todo]
    total: int
    limit: int
    offset: int
