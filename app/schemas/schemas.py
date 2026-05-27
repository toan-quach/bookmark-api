import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator

_TAG_RE = re.compile(r"^[a-z0-9]+(?:[_-][a-z0-9]+)*$")


class TagBase(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("Tag name must not be empty")
        if len(v) > 50:
            raise ValueError("Tag name must be 50 characters or fewer")
        if not _TAG_RE.match(v):
            raise ValueError("Tag name may only contain lowercase letters, digits, hyphens, and underscores")
        return v


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class UserBase(BaseModel):
    username: str
    email: str

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 30:
            raise ValueError("Username must be 30 characters or fewer")
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username may only contain letters, digits, hyphens, and underscores")
        return v

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Invalid email address")
        return v


class UserRegister(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class BookmarkBase(BaseModel):
    url: HttpUrl
    title: str
    description: str = ""

    @field_validator("title")
    @classmethod
    def title_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title must not be empty")
        if len(v) > 500:
            raise ValueError("Title must be 500 characters or fewer")
        return v

    @field_validator("description")
    @classmethod
    def description_length(cls, v: str) -> str:
        if len(v) > 5000:
            raise ValueError("Description must be 5000 characters or fewer")
        return v


class BookmarkCreate(BookmarkBase):
    tag_names: list[str] = []

    @field_validator("tag_names")
    @classmethod
    def validate_tag_names(cls, v: list[str]) -> list[str]:
        if len(v) > 20:
            raise ValueError("A bookmark may have at most 20 tags")
        seen: set[str] = set()
        cleaned: list[str] = []
        for name in v:
            name = name.strip().lower()
            if not name:
                continue
            if not _TAG_RE.match(name):
                raise ValueError(f"Invalid tag name: '{name}'")
            if name not in seen:
                seen.add(name)
                cleaned.append(name)
        return cleaned


class BookmarkUpdate(BaseModel):
    url: HttpUrl | None = None
    title: str | None = None
    description: str | None = None
    tag_names: list[str] | None = None

    @field_validator("title")
    @classmethod
    def title_must_be_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Title must not be empty")
        if len(v) > 500:
            raise ValueError("Title must be 500 characters or fewer")
        return v

    @field_validator("description")
    @classmethod
    def description_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 5000:
            raise ValueError("Description must be 5000 characters or fewer")
        return v

    @field_validator("tag_names")
    @classmethod
    def validate_tag_names(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        if len(v) > 20:
            raise ValueError("A bookmark may have at most 20 tags")
        seen: set[str] = set()
        cleaned: list[str] = []
        for name in v:
            name = name.strip().lower()
            if not name:
                continue
            if not _TAG_RE.match(name):
                raise ValueError(f"Invalid tag name: '{name}'")
            if name not in seen:
                seen.add(name)
                cleaned.append(name)
        return cleaned


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    error: str
    details: list[ErrorDetail] = []


class BookmarkRead(BookmarkBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    tags: list[TagRead] = []


class PaginatedBookmarks(BaseModel):
    items: list[BookmarkRead]
    total: int
    page: int
    page_size: int
