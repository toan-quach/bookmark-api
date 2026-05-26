from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import TokenResponse, UserRead, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.username == payload.username)):
        raise HTTPException(409, "Username already taken")
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(409, "Email already registered")
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == form.username))
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    return TokenResponse(access_token=create_access_token(user.id))
