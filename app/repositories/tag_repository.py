from sqlalchemy.orm import Session
from app.models.todo import Tag
from app.schemas.todo import TagBase
from typing import List, Optional

class TagRepository:
    def create(self, tag: TagBase, db: Session) -> Tag:
        db_tag = Tag(**tag.dict())
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag
    
    def get_all(self, db: Session) -> List[Tag]:
        return db.query(Tag).all()
    
    def get_by_id(self, tag_id: int, db: Session) -> Optional[Tag]:
        return db.query(Tag).filter(Tag.id == tag_id).first()
    
    def get_by_name(self, name: str, db: Session) -> Optional[Tag]:
        return db.query(Tag).filter(Tag.name == name).first()
    
    def get_or_create(self, tag_name: str, db: Session) -> Tag:
        tag = self.get_by_name(tag_name, db)
        if not tag:
            tag = self.create(TagBase(name=tag_name), db)
        return tag
