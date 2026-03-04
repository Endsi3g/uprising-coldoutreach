"""Pipeline endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import pipelines as pipe_crud
from app.schemas import PipelineCreate, PipelineOut, PipelineStageOut

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


@router.get("", response_model=list[PipelineOut])
def list_pipelines(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return pipe_crud.list_pipelines(db, user["account_id"])


@router.post("", response_model=PipelineOut, status_code=201)
def create_pipeline(body: PipelineCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return pipe_crud.create_pipeline(db, user["account_id"], body.name)


@router.get("/{pipeline_id}/stages", response_model=list[PipelineStageOut])
def list_stages(
    pipeline_id: uuid.UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pipeline = pipe_crud.get_pipeline(db, pipeline_id)
    if not pipeline or pipeline.account_id != user["account_id"]:
        raise HTTPException(404, "Pipeline not found")
    return pipe_crud.list_stages(db, pipeline_id)
