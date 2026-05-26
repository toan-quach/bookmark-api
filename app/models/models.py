from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


bookmark_tags = Table(
    "bookmark_tags",
    Base.metadata,
    Column("bookmark_id", Integer, ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True)
    url = Column(String(2048), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(500), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="bookmarks")
    tags = relationship("Tag", secondary=bookmark_tags, back_populates="bookmarks")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    bookmarks = relationship("Bookmark", secondary=bookmark_tags, back_populates="tags")
