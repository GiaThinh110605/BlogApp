from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base

class SoftDeleteMixin:
    """Mixin cho soft delete functionality"""
    
    @declared_attr
    def deleted_at(cls):
        return Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self):
        """Thực hiện soft delete"""
        self.deleted_at = func.now()
    
    def restore(self):
        """Khôi phục từ soft delete"""
        self.deleted_at = None
    
    @property
    def is_deleted(self):
        """Kiểm tra đã bị xóa chưa"""
        return self.deleted_at is not None
