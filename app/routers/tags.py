from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Tag
from app.schemas.schemas import TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("", response_model=TagRead, status_code=201, summary="Create a tag")
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Tag).where(Tag.name == payload.name)):
        raise HTTPException(409, "Tag already exists")
    tag = Tag(name=payload.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.get("", response_model=list[TagRead], summary="List all tags")
def list_tags(db: Session = Depends(get_db)):
    return list(db.scalars(select(Tag).order_by(Tag.name)).all())
