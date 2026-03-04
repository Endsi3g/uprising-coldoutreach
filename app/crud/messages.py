"""CRUD operations for Messages."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import Activity, Message


def create_message(db: Session, **kwargs) -> Message:
    msg = Message(**kwargs)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_message(db: Session, message_id: uuid.UUID) -> Message | None:
    return db.get(Message, message_id)


def update_message_status(db: Session, message: Message, status: str) -> Message:
    message.status = status
    message.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(message)
    return message


def list_messages_by_lead(db: Session, lead_id: uuid.UUID) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.lead_id == lead_id)
        .order_by(Message.created_at.desc())
        .all()
    )


def list_messages(db: Session, account_id: uuid.UUID) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.account_id == account_id)
        .order_by(Message.created_at.desc())
        .all()
    )


def record_activity(
    db: Session,
    account_id: uuid.UUID,
    lead_id: uuid.UUID,
    activity_type: str,
    data: dict | None = None,
) -> Activity:
    activity = Activity(
        account_id=account_id,
        lead_id=lead_id,
        type=activity_type,
        data=data or {},
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity
