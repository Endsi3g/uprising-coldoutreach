"""Integration endpoints — Gmail OAuth, Instagram OAuth, connect channels."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import OutboundIdentity
from app.services import gmail as gmail_svc
from app.services import instagram as ig_svc

router = APIRouter(prefix="/integrations", tags=["Integrations"])


# ── Gmail OAuth ─────────────────────────────────────────────────────────────


@router.post("/gmail/connect")
def gmail_connect(user: dict = Depends(get_current_user)):
    """Get the Gmail OAuth consent URL to connect a Gmail account."""
    try:
        url = gmail_svc.get_auth_url()
        return {"auth_url": url}
    except Exception as e:
        raise HTTPException(500, f"Failed to generate auth URL: {e}")


@router.get("/gmail/callback")
def gmail_callback(
    code: str = Query(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Handle Gmail OAuth callback — exchange code for tokens and create identity."""
    try:
        tokens = gmail_svc.exchange_code(code)
    except Exception as e:
        raise HTTPException(400, f"Token exchange failed: {e}")

    access_token = tokens.get("access_token", "")
    refresh_token = tokens.get("refresh_token", "")

    # Get user email
    try:
        email_addr = gmail_svc.get_user_email(access_token)
    except Exception:
        email_addr = "unknown@gmail.com"

    # Check if identity already exists
    existing = (
        db.query(OutboundIdentity)
        .filter(
            OutboundIdentity.account_id == user["account_id"],
            OutboundIdentity.type == "gmail_api",
            OutboundIdentity.label == email_addr,
        )
        .first()
    )

    if existing:
        # Update tokens
        existing.config = {
            **existing.config,
            "access_token": access_token,
            "refresh_token": refresh_token or existing.config.get("refresh_token", ""),
            "from_email": email_addr,
        }
        db.commit()
        db.refresh(existing)
        return {"status": "updated", "identity_id": str(existing.id), "email": email_addr}

    # Create new outbound identity
    identity = OutboundIdentity(
        id=uuid.uuid4(),
        account_id=user["account_id"],
        type="gmail_api",
        label=email_addr,
        config={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "from_email": email_addr,
            "from_name": "",
        },
        is_default=False,
        daily_limit=500,
    )
    db.add(identity)
    db.commit()
    db.refresh(identity)

    return {"status": "connected", "identity_id": str(identity.id), "email": email_addr}


# ── Instagram OAuth ─────────────────────────────────────────────────────────


@router.post("/instagram/connect")
def instagram_connect(user: dict = Depends(get_current_user)):
    """Get the Instagram/Facebook OAuth consent URL."""
    try:
        url = ig_svc.get_auth_url()
        return {"auth_url": url}
    except Exception as e:
        raise HTTPException(500, f"Failed to generate auth URL: {e}")


@router.get("/instagram/callback")
def instagram_callback(
    code: str = Query(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Handle Instagram OAuth callback — exchange code and create identity."""
    try:
        tokens = ig_svc.exchange_code(code)
    except Exception as e:
        raise HTTPException(400, f"Token exchange failed: {e}")

    access_token = tokens.get("access_token", "")

    # Get Instagram business account info
    try:
        ig_info = ig_svc.get_instagram_business_account(access_token)
    except Exception as e:
        raise HTTPException(400, f"Failed to get IG account: {e}")

    ig_account_id = ig_info.get("ig_account_id", "")
    page_token = ig_info.get("page_access_token", access_token)

    # Check if identity exists
    existing = (
        db.query(OutboundIdentity)
        .filter(
            OutboundIdentity.account_id == user["account_id"],
            OutboundIdentity.type == "instagram_dm",
        )
        .first()
    )

    if existing:
        existing.config = {
            **existing.config,
            "access_token": page_token,
            "ig_account_id": ig_account_id,
            "page_id": ig_info.get("page_id", ""),
        }
        db.commit()
        db.refresh(existing)
        return {"status": "updated", "identity_id": str(existing.id), "ig_account_id": ig_account_id}

    identity = OutboundIdentity(
        id=uuid.uuid4(),
        account_id=user["account_id"],
        type="instagram_dm",
        label=f"Instagram ({ig_account_id})",
        config={
            "access_token": page_token,
            "ig_account_id": ig_account_id,
            "page_id": ig_info.get("page_id", ""),
        },
        is_default=False,
        daily_limit=100,
    )
    db.add(identity)
    db.commit()
    db.refresh(identity)

    return {"status": "connected", "identity_id": str(identity.id), "ig_account_id": ig_account_id}
