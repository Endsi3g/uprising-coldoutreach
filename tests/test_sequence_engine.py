"""Test sequence engine — full 3-step flow."""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.crud import sequences as seq_crud
from app.models import SequenceEnrollment


def test_create_enrollment(db_session, seed_sequence, seed_lead):
    seq, steps = seed_sequence
    enrollment = seq_crud.create_enrollment(db_session, seq.id, seed_lead.id, start_immediately=True)
    assert enrollment.status == "running"
    assert enrollment.current_step_index == 0
    assert enrollment.next_run_at is not None


def test_bulk_enroll_skips_duplicates(db_session, seed_sequence, seed_lead):
    seq, steps = seed_sequence
    # First enrollment
    results1 = seq_crud.bulk_enroll(db_session, seq.id, [seed_lead.id], start_immediately=True)
    assert len(results1) == 1
    # Second enrollment — should skip
    results2 = seq_crud.bulk_enroll(db_session, seq.id, [seed_lead.id], start_immediately=True)
    assert len(results2) == 0


def test_get_due_enrollments(db_session, seed_sequence, seed_lead):
    seq, steps = seed_sequence
    enrollment = seq_crud.create_enrollment(db_session, seq.id, seed_lead.id, start_immediately=True)
    # It should be due immediately
    due = seq_crud.get_due_enrollments(db_session)
    assert len(due) >= 1
    assert any(e.id == enrollment.id for e in due)


def test_advance_enrollment(db_session, seed_sequence, seed_lead):
    seq, steps = seed_sequence
    enrollment = seq_crud.create_enrollment(db_session, seq.id, seed_lead.id, start_immediately=True)
    advanced = seq_crud.advance_enrollment(db_session, enrollment, 1, wait_hours=24)
    assert advanced.current_step_index == 1
    # Handle possible naive datetime from SQLite
    next_run = advanced.next_run_at
    if next_run.tzinfo is None:
        from datetime import timezone as tz
        next_run = next_run.replace(tzinfo=tz.utc)
    assert next_run > datetime.now(timezone.utc)


def test_complete_enrollment(db_session, seed_sequence, seed_lead):
    seq, steps = seed_sequence
    enrollment = seq_crud.create_enrollment(db_session, seq.id, seed_lead.id, start_immediately=True)
    completed = seq_crud.complete_enrollment(db_session, enrollment)
    assert completed.status == "completed"
    assert completed.next_run_at is None


def test_list_steps_ordered(db_session, seed_sequence):
    seq, steps = seed_sequence
    listed = seq_crud.list_steps(db_session, seq.id)
    assert len(listed) == 3
    assert listed[0].type == "email"
    assert listed[1].type == "wait"
    assert listed[2].type == "email"
    assert listed[0].order_index < listed[1].order_index < listed[2].order_index
