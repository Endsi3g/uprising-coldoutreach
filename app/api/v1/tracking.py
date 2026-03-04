"""Tracking endpoints – open pixel and click redirect (public, no auth)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import messages as msg_crud

router = APIRouter(prefix="/track", tags=["Tracking"])

# 1x1 transparent GIF
PIXEL_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00"
    b"\xff\xff\xff\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00"
    b",\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


@router.get("/open/{message_id}")
def track_open(message_id: uuid.UUID, db: Session = Depends(get_db)):
    """Record email open and return transparent pixel."""
    msg = msg_crud.get_message(db, message_id)
    if msg and msg.status in ("sent", "delivered"):
        msg_crud.update_message_status(db, msg, "opened")
        msg_crud.record_activity(
            db, msg.account_id, msg.lead_id, "email_opened",
            {"message_id": str(message_id)},
        )
    return Response(content=PIXEL_GIF, media_type="image/gif")


@router.get("/click/{message_id}")
def track_click(message_id: uuid.UUID, url: str = Query(...), db: Session = Depends(get_db)):
    """Record link click and redirect to original URL."""
    msg = msg_crud.get_message(db, message_id)
    if msg and msg.status in ("sent", "delivered", "opened"):
        msg_crud.update_message_status(db, msg, "clicked")
        msg_crud.record_activity(
            db, msg.account_id, msg.lead_id, "email_clicked",
            {"message_id": str(message_id), "url": url},
        )
    return RedirectResponse(url=url)
