from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Todo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_done = Column(Boolean, default=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship để dễ truy cập user từ todo
    owner = relationship("User", back_populates="todos")
    
    # Many-to-many relationship with tags
    tags = relationship("Tag", secondary="todo_tags", back_populates="todos")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default="#000000")  # Hex color
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    todos = relationship("Todo", secondary="todo_tags", back_populates="tags")

class TodoTag(Base):
    __tablename__ = "todo_tags"
    
    todo_id = Column(Integer, ForeignKey("todos.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
