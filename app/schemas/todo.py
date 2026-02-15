from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class TodoBase(BaseModel):
    title: str
    is_done: bool = False
    
    @validator('title')
    def title_length(cls, v):
        if not v or len(v) < 3 or len(v) > 100:
            raise ValueError('Title must be 3-100 characters')
        return v


class TodoCreate(TodoBase):
    id: int


class TodoUpdate(TodoBase):
    pass


class Todo(TodoBase):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True


class TodoResponse(BaseModel):
    items: list[Todo]
    total: int
    limit: int
    offset: int
