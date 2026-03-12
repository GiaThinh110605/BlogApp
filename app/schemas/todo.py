from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List

class TagBase(BaseModel):
    name: str
    color: str = "#000000"

class Tag(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TodoBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_done: bool = False

class TodoCreate(TodoBase):
    tag_ids: Optional[List[int]] = []

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_done: Optional[bool] = None
    tag_ids: Optional[List[int]] = None

class Todo(TodoBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    tags: List[Tag] = []
    
    class Config:
        from_attributes = True

class TodoResponse(BaseModel):
    items: list[Todo]
    total: int
    limit: int
    offset: int
