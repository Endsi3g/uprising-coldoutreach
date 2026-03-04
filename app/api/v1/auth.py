"""Auth endpoints – login, JWT tokens."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import Account, User
from app.schemas import (
    AccountCreate,
    AccountOut,
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserOut,
)

router = APIRouter(tags=["Auth"])


# ── Registration (account + first user) ─────────────────────────────────────

@router.post("/auth/register", response_model=UserOut, status_code=201)
def register(body: AccountCreate, user: UserCreate, db: Session = Depends(get_db)):
    # check duplicate email
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    account = Account(name=body.name, time_zone=body.time_zone)
    db.add(account)
    db.flush()
    new_user = User(
        account_id=account.id,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ── Login ───────────────────────────────────────────────────────────────────

@router.post("/auth/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    data = {"sub": str(user.id), "account_id": str(user.account_id), "role": user.role}
    return TokenResponse(
        access_token=create_access_token(data),
        refresh_token=create_refresh_token(data),
    )
