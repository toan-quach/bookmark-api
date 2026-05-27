from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.auth import get_current_user
from app.db.session import get_db
from app.models.models import Bookmark, Tag, User
from app.schemas.schemas import BookmarkCreate, BookmarkRead, BookmarkUpdate, PaginatedBookmarks

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


def _get_or_create_tags(db: Session, names: list[str]) -> list[Tag]:
    tags = []
    for name in names:
        name = name.strip().lower()
        if not name:
            continue
        tag = db.scalar(select(Tag).where(Tag.name == name))
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


@router.post("", response_model=BookmarkRead, status_code=201, summary="Create a bookmark")
def create_bookmark(
    payload: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = Bookmark(
        url=str(payload.url),
        title=payload.title,
        description=payload.description,
        user_id=current_user.id,
    )
    if payload.tag_names:
        bookmark.tags = _get_or_create_tags(db, payload.tag_names)
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.get("", response_model=PaginatedBookmarks, summary="List bookmarks with filters and pagination")
def list_bookmarks(
    tag: str | None = Query(None, description="Filter by tag name"),
    q: str | None = Query(None, description="Search title keyword"),
    created_after: datetime | None = Query(None, description="Filter bookmarks created after this datetime"),
    created_before: datetime | None = Query(None, description="Filter bookmarks created before this datetime"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    base = select(Bookmark).where(Bookmark.user_id == current_user.id)

    if tag:
        base = base.join(Bookmark.tags).where(Tag.name == tag.strip().lower())
    if q:
        base = base.where(Bookmark.title.ilike(f"%{q}%"))
    if created_after:
        if created_after.tzinfo is None:
            created_after = created_after.replace(tzinfo=timezone.utc)
        base = base.where(Bookmark.created_at >= created_after)
    if created_before:
        if created_before.tzinfo is None:
            created_before = created_before.replace(tzinfo=timezone.utc)
        base = base.where(Bookmark.created_at <= created_before)

    total = db.scalar(select(func.count()).select_from(base.subquery()))

    stmt = (
        base
        .options(selectinload(Bookmark.tags))
        .order_by(Bookmark.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.scalars(stmt).unique().all())

    return PaginatedBookmarks(items=items, total=total, page=page, page_size=page_size)


@router.get("/{bookmark_id}", response_model=BookmarkRead, summary="Get a bookmark by ID")
def get_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = db.scalar(
        select(Bookmark)
        .options(selectinload(Bookmark.tags))
        .where(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id)
    )
    if not bookmark:
        raise HTTPException(404, "Bookmark not found")
    return bookmark


@router.patch("/{bookmark_id}", response_model=BookmarkRead, summary="Update a bookmark")
def update_bookmark(
    bookmark_id: int,
    payload: BookmarkUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = db.scalar(
        select(Bookmark)
        .options(selectinload(Bookmark.tags))
        .where(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id)
    )
    if not bookmark:
        raise HTTPException(404, "Bookmark not found")

    if payload.url is not None:
        bookmark.url = str(payload.url)
    if payload.title is not None:
        bookmark.title = payload.title
    if payload.description is not None:
        bookmark.description = payload.description
    if payload.tag_names is not None:
        bookmark.tags = _get_or_create_tags(db, payload.tag_names)

    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.delete("/{bookmark_id}", status_code=204, summary="Delete a bookmark")
def delete_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = db.scalar(
        select(Bookmark).where(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id)
    )
    if not bookmark:
        raise HTTPException(404, "Bookmark not found")
    db.delete(bookmark)
    db.commit()
