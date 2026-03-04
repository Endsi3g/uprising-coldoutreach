"""Google Maps jobs – trigger Apify scrape, check status."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import leads as leads_crud
from app.crud import pipelines as pipe_crud
from app.models import LeadSource
from app.schemas import GoogleMapsJobRequest, GoogleMapsJobOut
from app.services import apify as apify_svc
from app.services.scoring import compute_icp_score

router = APIRouter(prefix="/google-maps-jobs", tags=["Google Maps"])


# In-memory job store (upgrade to DB table for production)
_jobs: dict[str, dict] = {}


@router.post("", status_code=201)
def create_job(
    body: GoogleMapsJobRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Launch an Apify Google Maps scrape."""
    # Create a lead source record
    source = LeadSource(
        account_id=user["account_id"],
        type="google_maps",
        metadata_={
            "query": body.query,
            "location": body.location,
            "max_items": body.max_items,
            "radius_km": body.radius_km,
        },
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    # Start Apify run
    try:
        run_data = apify_svc.start_google_maps_run(
            query=body.query,
            location=body.location,
            max_items=body.max_items,
        )
    except Exception as e:
        raise HTTPException(502, f"Apify error: {e}")

    run_id = run_data.get("id", "")
    dataset_id = run_data.get("defaultDatasetId", "")

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "account_id": str(user["account_id"]),
        "source_id": str(source.id),
        "apify_run_id": run_id,
        "dataset_id": dataset_id,
        "status": "running",
        "query": body.query,
        "location": body.location,
        "max_items": body.max_items,
        "leads_created": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return {"job_id": job_id, "apify_run_id": run_id, "status": "running"}


@router.get("/{job_id}")
def get_job(job_id: str, user: dict = Depends(get_current_user)):
    job = _jobs.get(job_id)
    if not job or job["account_id"] != str(user["account_id"]):
        raise HTTPException(404, "Job not found")
    return job


@router.post("/{job_id}/poll")
def poll_job(
    job_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Poll Apify for results and create leads."""
    job = _jobs.get(job_id)
    if not job or job["account_id"] != str(user["account_id"]):
        raise HTTPException(404, "Job not found")

    if job["status"] == "completed":
        return {"status": "completed", "leads_created": job["leads_created"]}

    # Check run status
    try:
        run_data = apify_svc.get_run_status(job["apify_run_id"])
    except Exception as e:
        raise HTTPException(502, f"Apify error: {e}")

    apify_status = run_data.get("status", "RUNNING")
    if apify_status not in ("SUCCEEDED",):
        return {"status": apify_status.lower(), "leads_created": 0}

    # Fetch dataset items
    try:
        items = apify_svc.get_dataset_items(job["dataset_id"], limit=job["max_items"])
    except Exception as e:
        raise HTTPException(502, f"Dataset error: {e}")

    # Normalize and create leads
    account_id = uuid.UUID(job["account_id"])
    source_id = uuid.UUID(job["source_id"])

    # Get or create default pipeline
    pipelines = pipe_crud.list_pipelines(db, account_id)
    if pipelines:
        pipeline = pipelines[0]
    else:
        pipeline = pipe_crud.create_pipeline(db, account_id, "Default Pipeline")
    default_stage = pipe_crud.get_default_stage(db, pipeline.id)

    normalized = [apify_svc.normalize_place(item) for item in items]

    # Compute ICP scores
    for n in normalized:
        n["icp_score"] = compute_icp_score(
            industry=n.get("industry"),
            city=n.get("city"),
            website=n.get("website"),
            phone=n.get("phone"),
        )

    leads = leads_crud.bulk_create_leads(
        db, account_id, normalized,
        source_id=source_id,
        pipeline_id=pipeline.id,
        stage_id=default_stage.id if default_stage else None,
    )

    job["status"] = "completed"
    job["leads_created"] = len(leads)
    return {"status": "completed", "leads_created": len(leads)}
