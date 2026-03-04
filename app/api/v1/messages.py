"""Message endpoints – send, bulk-send, list by lead."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import messages as msg_crud
from app.models import OutboundIdentity
from app.schemas import MessageOut, MessageSendRequest
from app.services.email import prepare_html, send_smtp_email

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/send", response_model=MessageOut, status_code=201)
def send_message(
    body: MessageSendRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    identity = db.get(OutboundIdentity, body.identity_id)
    if not identity or identity.account_id != user["account_id"]:
        raise HTTPException(404, "Identity not found")

    # Check daily limit
    if identity.used_today >= identity.daily_limit:
        raise HTTPException(429, "Daily send limit reached")

    # Create message record
    msg = msg_crud.create_message(
        db,
        account_id=user["account_id"],
        lead_id=body.lead_id,
        direction="outbound",
        channel="email",
        from_identity_id=identity.id,
        to_email=body.to_email,
        subject=body.subject,
        body_html=body.body_html,
        status="queued",
    )

    # Prepare HTML with tracking
    final_html = prepare_html(
        body.body_html, msg.id,
        add_pixel=body.tracking_pixel,
        track_clicks=body.track_clicks,
    )

    # Send via SMTP
    success = send_smtp_email(identity.config, body.to_email, body.subject, final_html)

    if success:
        msg_crud.update_message_status(db, msg, "sent")
        identity.used_today += 1
        db.commit()
        msg_crud.record_activity(
            db, user["account_id"], body.lead_id, "email_sent",
            {"message_id": str(msg.id), "to": body.to_email},
        )
    else:
        msg_crud.update_message_status(db, msg, "failed")

    db.refresh(msg)
    return msg


@router.get("/lead/{lead_id}", response_model=list[MessageOut])
def list_lead_messages(
    lead_id: uuid.UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return msg_crud.list_messages_by_lead(db, lead_id)
