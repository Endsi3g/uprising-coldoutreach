"""CRUD operations for Sequences, Steps, Enrollments."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Sequence, SequenceEnrollment, SequenceStep


# ── Sequences ───────────────────────────────────────────────────────────────

def create_sequence(db: Session, account_id: uuid.UUID, name: str, description: str | None = None) -> Sequence:
    seq = Sequence(account_id=account_id, name=name, description=description)
    db.add(seq)
    db.commit()
    db.refresh(seq)
    return seq


def list_sequences(db: Session, account_id: uuid.UUID) -> list[Sequence]:
    return db.query(Sequence).filter(Sequence.account_id == account_id).order_by(Sequence.created_at.desc()).all()


def get_sequence(db: Session, seq_id: uuid.UUID) -> Sequence | None:
    return db.get(Sequence, seq_id)


# ── Steps ───────────────────────────────────────────────────────────────────

def create_step(db: Session, sequence_id: uuid.UUID, **kwargs) -> SequenceStep:
    step = SequenceStep(sequence_id=sequence_id, **kwargs)
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def list_steps(db: Session, sequence_id: uuid.UUID) -> list[SequenceStep]:
    return (
        db.query(SequenceStep)
        .filter(SequenceStep.sequence_id == sequence_id)
        .order_by(SequenceStep.order_index)
        .all()
    )


# ── Enrollments ─────────────────────────────────────────────────────────────

def create_enrollment(
    db: Session,
    sequence_id: uuid.UUID,
    lead_id: uuid.UUID,
    start_immediately: bool = True,
) -> SequenceEnrollment:
    enrollment = SequenceEnrollment(
        sequence_id=sequence_id,
        lead_id=lead_id,
        status="running" if start_immediately else "pending",
        current_step_index=0,
        next_run_at=datetime.now(timezone.utc) if start_immediately else None,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def bulk_enroll(
    db: Session,
    sequence_id: uuid.UUID,
    lead_ids: list[uuid.UUID],
    start_immediately: bool = True,
) -> list[SequenceEnrollment]:
    enrollments = []
    for lid in lead_ids:
        # skip already enrolled
        existing = (
            db.query(SequenceEnrollment)
            .filter(
                SequenceEnrollment.sequence_id == sequence_id,
                SequenceEnrollment.lead_id == lid,
                SequenceEnrollment.status.in_(["pending", "running"]),
            )
            .first()
        )
        if existing:
            continue
        e = create_enrollment(db, sequence_id, lid, start_immediately)
        enrollments.append(e)
    return enrollments


def get_due_enrollments(db: Session) -> list[SequenceEnrollment]:
    """Return enrollments that are running and due for processing."""
    now = datetime.now(timezone.utc)
    return (
        db.query(SequenceEnrollment)
        .filter(
            SequenceEnrollment.status == "running",
            SequenceEnrollment.next_run_at <= now,
        )
        .all()
    )


def advance_enrollment(
    db: Session,
    enrollment: SequenceEnrollment,
    next_step_index: int,
    wait_hours: int = 0,
) -> SequenceEnrollment:
    enrollment.current_step_index = next_step_index
    enrollment.next_run_at = datetime.now(timezone.utc) + timedelta(hours=wait_hours)
    enrollment.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def complete_enrollment(db: Session, enrollment: SequenceEnrollment) -> SequenceEnrollment:
    enrollment.status = "completed"
    enrollment.next_run_at = None
    enrollment.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(enrollment)
    return enrollment
