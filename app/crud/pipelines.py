"""CRUD operations for Pipelines & Stages."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models import Pipeline, PipelineStage


DEFAULT_STAGES = [
    ("New", 0, "#6B7280"),
    ("Contacted", 1, "#3B82F6"),
    ("Replied", 2, "#8B5CF6"),
    ("Hot", 3, "#EF4444"),
    ("Booked", 4, "#F59E0B"),
    ("Closed Won", 5, "#10B981"),
    ("Closed Lost", 6, "#6B7280"),
]


def create_pipeline(db: Session, account_id: uuid.UUID, name: str) -> Pipeline:
    pipeline = Pipeline(account_id=account_id, name=name)
    db.add(pipeline)
    db.flush()
    # create default stages
    for stage_name, order, color in DEFAULT_STAGES:
        stage = PipelineStage(
            pipeline_id=pipeline.id, name=stage_name, order_index=order, color=color,
        )
        db.add(stage)
    db.commit()
    db.refresh(pipeline)
    return pipeline


def list_pipelines(db: Session, account_id: uuid.UUID) -> list[Pipeline]:
    return db.query(Pipeline).filter(Pipeline.account_id == account_id).all()


def get_pipeline(db: Session, pipeline_id: uuid.UUID) -> Pipeline | None:
    return db.get(Pipeline, pipeline_id)


def list_stages(db: Session, pipeline_id: uuid.UUID) -> list[PipelineStage]:
    return (
        db.query(PipelineStage)
        .filter(PipelineStage.pipeline_id == pipeline_id)
        .order_by(PipelineStage.order_index)
        .all()
    )


def get_stage(db: Session, stage_id: uuid.UUID) -> PipelineStage | None:
    return db.get(PipelineStage, stage_id)


def get_default_stage(db: Session, pipeline_id: uuid.UUID) -> PipelineStage | None:
    """Return the first stage (order_index=0) of a pipeline."""
    return (
        db.query(PipelineStage)
        .filter(PipelineStage.pipeline_id == pipeline_id)
        .order_by(PipelineStage.order_index)
        .first()
    )
