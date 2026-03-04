"""CRUD operations for Leads."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Activity, Lead, LeadSource


def create_lead(db: Session, account_id: uuid.UUID, **kwargs) -> Lead:
    lead = Lead(account_id=account_id, **kwargs)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def bulk_create_leads(
    db: Session,
    account_id: uuid.UUID,
    items: list[dict],
    source_id: uuid.UUID | None = None,
    pipeline_id: uuid.UUID | None = None,
    stage_id: uuid.UUID | None = None,
) -> list[Lead]:
    leads = []
    for item in items:
        lead = Lead(
            account_id=account_id,
            source_id=source_id,
            pipeline_id=pipeline_id,
            stage_id=stage_id,
            **item,
        )
        db.add(lead)
        leads.append(lead)
    db.commit()
    for lead in leads:
        db.refresh(lead)
    # update source leads_count
    if source_id:
        src = db.get(LeadSource, source_id)
        if src:
            src.leads_count = (src.leads_count or 0) + len(leads)
            db.commit()
    return leads


def get_lead(db: Session, lead_id: uuid.UUID) -> Lead | None:
    return db.get(Lead, lead_id)


def list_leads(
    db: Session,
    account_id: uuid.UUID,
    pipeline_id: uuid.UUID | None = None,
    stage_id: uuid.UUID | None = None,
    city: str | None = None,
    icp_score_gte: int | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Lead]:
    q = db.query(Lead).filter(Lead.account_id == account_id)
    if pipeline_id:
        q = q.filter(Lead.pipeline_id == pipeline_id)
    if stage_id:
        q = q.filter(Lead.stage_id == stage_id)
    if city:
        q = q.filter(Lead.city.ilike(f"%{city}%"))
    if icp_score_gte is not None:
        q = q.filter(Lead.icp_score >= icp_score_gte)
    if status:
        q = q.filter(Lead.status == status)
    return q.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


def update_lead(db: Session, lead: Lead, data: dict) -> Lead:
    for k, v in data.items():
        if v is not None:
            setattr(lead, k, v)
    lead.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lead)
    return lead


def move_stage(
    db: Session,
    lead: Lead,
    new_stage_id: uuid.UUID,
    account_id: uuid.UUID,
) -> Lead:
    old_stage_id = lead.stage_id
    lead.stage_id = new_stage_id
    lead.updated_at = datetime.now(timezone.utc)
    activity = Activity(
        account_id=account_id,
        lead_id=lead.id,
        type="stage_changed",
        data={"from_stage_id": str(old_stage_id), "to_stage_id": str(new_stage_id)},
    )
    db.add(activity)
    db.commit()
    db.refresh(lead)
    return lead


def count_leads(db: Session, account_id: uuid.UUID) -> int:
    return db.query(func.count(Lead.id)).filter(Lead.account_id == account_id).scalar() or 0
