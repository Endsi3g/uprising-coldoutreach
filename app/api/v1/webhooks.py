"""Webhook receiver — inbound reply notifications and external events."""

from __future__ import annotations

import hashlib
import hmac
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.crud import messages as msg_crud
from app.models import Lead, SequenceEnrollment

logger = logging.getLogger("webhooks")

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/reply")
async def receive_reply(
    request: Request,
    db: Session = Depends(get_db),
):
    """Receive inbound reply notifications.

    Expected payload:
    {
        "from_email": "lead@example.com",
        "subject": "Re: ...",
        "body_text": "...",
        "provider_message_id": "optional",
        "signature": "hmac-sha256 of body (optional)"
    }
    """
    body = await request.json()

    # Optional webhook signature validation
    webhook_secret = getattr(settings, "WEBHOOK_SECRET", "")
    if webhook_secret:
        provided_sig = body.get("signature", "")
        # Compute expected signature from payload minus the signature field
        payload_str = str({k: v for k, v in body.items() if k != "signature"})
        expected_sig = hmac.new(
            webhook_secret.encode(), payload_str.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(provided_sig, expected_sig):
            raise HTTPException(401, "Invalid webhook signature")

    from_email = body.get("from_email", "").strip().lower()
    if not from_email:
        raise HTTPException(400, "from_email is required")

    subject = body.get("subject", "")
    body_text = body.get("body_text", "")

    # Find matching lead by email
    lead = db.query(Lead).filter(Lead.email == from_email).first()
    if not lead:
        logger.info(f"Webhook reply from unknown email: {from_email}")
        return {"status": "ignored", "reason": "no matching lead"}

    # Create inbound message
    msg = msg_crud.create_message(
        db,
        account_id=lead.account_id,
        lead_id=lead.id,
        direction="inbound",
        channel="email",
        from_identity_id=None,
        to_email=None,
        subject=subject,
        body_html=None,
        body_text=body_text,
        status="received",
    )

    # Record activity
    msg_crud.record_activity(
        db, lead.account_id, lead.id, "reply_received",
        {"message_id": str(msg.id), "from_email": from_email},
    )

    # Update lead heat score
    lead.heat_score = min(100, lead.heat_score + 25)
    db.commit()

    # Pause any active enrollments for this lead
    active_enrollments = (
        db.query(SequenceEnrollment)
        .filter(
            SequenceEnrollment.lead_id == lead.id,
            SequenceEnrollment.status.in_(["pending", "running"]),
        )
        .all()
    )
    for enrollment in active_enrollments:
        enrollment.status = "paused"
    db.commit()

    logger.info(f"Webhook reply processed for lead {lead.id} from {from_email}")

    return {
        "status": "processed",
        "lead_id": str(lead.id),
        "message_id": str(msg.id),
        "enrollments_paused": len(active_enrollments),
    }
