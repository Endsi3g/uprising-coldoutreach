"""Analytics endpoints – overview and pipeline funnel."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import pipelines as pipe_crud
from app.models import Lead, Message, PipelineStage, Sequence
from app.schemas import AnalyticsOverview, PipelineFunnel, PipelineFunnelStage

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def overview(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    aid = user["account_id"]

    total_leads = db.query(func.count(Lead.id)).filter(Lead.account_id == aid).scalar() or 0
    active_sequences = (
        db.query(func.count(Sequence.id))
        .filter(Sequence.account_id == aid, Sequence.is_active.is_(True))
        .scalar() or 0
    )

    # Emails sent today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    emails_sent_today = (
        db.query(func.count(Message.id))
        .filter(
            Message.account_id == aid,
            Message.direction == "outbound",
            Message.created_at >= today_start,
        )
        .scalar() or 0
    )

    # Open/reply rate
    total_sent = (
        db.query(func.count(Message.id))
        .filter(Message.account_id == aid, Message.direction == "outbound")
        .scalar() or 1
    )
    total_opened = (
        db.query(func.count(Message.id))
        .filter(Message.account_id == aid, Message.status.in_(["opened", "clicked"]))
        .scalar() or 0
    )

    return AnalyticsOverview(
        total_leads=total_leads,
        active_sequences=active_sequences,
        emails_sent_today=emails_sent_today,
        open_rate=round(total_opened / max(total_sent, 1) * 100, 1),
        reply_rate=0.0,  # TODO: parse replies via IMAP
    )


@router.get("/pipeline-funnel/{pipeline_id}", response_model=PipelineFunnel)
def pipeline_funnel(
    pipeline_id: uuid.UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pipeline = pipe_crud.get_pipeline(db, pipeline_id)
    if not pipeline or pipeline.account_id != user["account_id"]:
        raise HTTPException(404, "Pipeline not found")

    stages = pipe_crud.list_stages(db, pipeline_id)
    result = []
    for stage in stages:
        count = (
            db.query(func.count(Lead.id))
            .filter(Lead.pipeline_id == pipeline_id, Lead.stage_id == stage.id)
            .scalar() or 0
        )
        result.append(PipelineFunnelStage(stage_name=stage.name, count=count, color=stage.color))

    return PipelineFunnel(pipeline_name=pipeline.name, stages=result)
