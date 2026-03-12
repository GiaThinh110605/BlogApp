from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.todo import TagBase, Tag
from app.repositories.tag_repository import TagRepository
from app.models.user import User

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("/", response_model=Tag)
def create_tag(
    tag: TagBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tag_repo = TagRepository()
    # Check if tag already exists
    existing = tag_repo.get_by_name(tag.name, db)
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")
    
    return tag_repo.create(tag, db)

@router.get("/", response_model=list[Tag])
def get_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tag_repo = TagRepository()
    return tag_repo.get_all(db)
