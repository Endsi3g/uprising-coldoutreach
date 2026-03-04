"""Sequence endpoints – CRUD, steps, enrollments."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import sequences as seq_crud
from app.schemas import (
    EnrollmentBulkRequest,
    EnrollmentOut,
    SequenceCreate,
    SequenceOut,
    SequenceStepCreate,
    SequenceStepOut,
)

router = APIRouter(prefix="/sequences", tags=["Sequences"])


@router.get("", response_model=list[SequenceOut])
def list_sequences(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return seq_crud.list_sequences(db, user["account_id"])


@router.post("", response_model=SequenceOut, status_code=201)
def create_sequence(body: SequenceCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return seq_crud.create_sequence(db, user["account_id"], body.name, body.description)


@router.get("/{seq_id}", response_model=SequenceOut)
def get_sequence(seq_id: uuid.UUID, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    seq = seq_crud.get_sequence(db, seq_id)
    if not seq or seq.account_id != user["account_id"]:
        raise HTTPException(404, "Sequence not found")
    return seq


# ── Steps ───────────────────────────────────────────────────────────────────

@router.get("/{seq_id}/steps", response_model=list[SequenceStepOut])
def list_steps(seq_id: uuid.UUID, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    seq = seq_crud.get_sequence(db, seq_id)
    if not seq or seq.account_id != user["account_id"]:
        raise HTTPException(404, "Sequence not found")
    return seq_crud.list_steps(db, seq_id)


@router.post("/{seq_id}/steps", response_model=SequenceStepOut, status_code=201)
def create_step(
    seq_id: uuid.UUID,
    body: SequenceStepCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    seq = seq_crud.get_sequence(db, seq_id)
    if not seq or seq.account_id != user["account_id"]:
        raise HTTPException(404, "Sequence not found")
    return seq_crud.create_step(db, seq_id, **body.model_dump())


# ── Enrollments ─────────────────────────────────────────────────────────────

@router.post("/{seq_id}/enrollments/bulk", response_model=list[EnrollmentOut], status_code=201)
def bulk_enroll(
    seq_id: uuid.UUID,
    body: EnrollmentBulkRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    seq = seq_crud.get_sequence(db, seq_id)
    if not seq or seq.account_id != user["account_id"]:
        raise HTTPException(404, "Sequence not found")
    return seq_crud.bulk_enroll(db, seq_id, body.lead_ids, body.start_immediately)
