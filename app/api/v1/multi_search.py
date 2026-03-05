"""Multi-search — batch Google Maps scraping across multiple queries/locations."""

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
from app.schemas import MultiSearchRequest, MultiSearchBatchOut
from app.services import apify as apify_svc
from app.services.scoring import compute_icp_score

router = APIRouter(prefix="/multi-search", tags=["Multi Search"])

# In-memory batch store (upgrade to DB for production)
_batches: dict[str, dict] = {}


import asyncio

@router.post("", status_code=201)
async def create_multi_search(
    body: MultiSearchRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Launch multiple Google Maps scrapes in batch."""
    if not body.searches or len(body.searches) == 0:
        raise HTTPException(400, "At least one search is required")
    if len(body.searches) > 20:
        raise HTTPException(400, "Maximum 20 searches per batch")

    batch_id = str(uuid.uuid4())
    sources = []
    
    # Pre-create sources in DB (synchronously for now, DB session is sync)
    for search in body.searches:
        source = LeadSource(
            account_id=user["account_id"],
            type="google_maps",
            metadata_={
                "query": search.query,
                "location": search.location,
                "max_items": search.max_items,
                "batch_id": batch_id,
            },
        )
        db.add(source)
        sources.append((source, search))
    
    db.commit()
    for s, _ in sources:
        db.refresh(s)

    # Parallelized Apify runs
    async def _start_job(source, search):
        try:
            run_data = await apify_svc.start_google_maps_run(
                query=search.query,
                location=search.location,
                max_items=search.max_items,
            )
            return {
                "query": search.query,
                "location": search.location,
                "status": "running",
                "apify_run_id": run_data.get("id", ""),
                "dataset_id": run_data.get("defaultDatasetId", ""),
                "source_id": str(source.id),
                "max_items": search.max_items,
                "leads_created": 0,
            }
        except Exception as e:
            return {
                "query": search.query,
                "location": search.location,
                "status": "error",
                "error": str(e),
                "source_id": str(source.id),
            }

    sub_jobs = await asyncio.gather(*[_start_job(s, search) for s, search in sources])

    _batches[batch_id] = {
        "id": batch_id,
        "account_id": str(user["account_id"]),
        "status": "running",
        "total_searches": len(body.searches),
        "completed": 0,
        "total_leads_created": 0,
        "sub_jobs": sub_jobs,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "batch_id": batch_id,
        "total_searches": len(body.searches),
        "status": "running",
        "sub_jobs_started": sum(1 for j in sub_jobs if j["status"] == "running"),
        "sub_jobs_errored": sum(1 for j in sub_jobs if j["status"] == "error"),
    }


@router.get("/history")
def get_batch_history(user: dict = Depends(get_current_user)):
    """Retrieve all search jobs for the current account."""
    return [
        {
            "id": b["id"],
            "status": b["status"].upper(), # Frontend expects UPPERCASE status
            "total_found": b["total_leads_created"],
            "search_queries": [j["query"] for j in b["sub_jobs"]],
            "created_at": b["created_at"]
        }
        for b in _batches.values()
        if b["account_id"] == str(user["account_id"])
    ]


@router.get("/{batch_id}")
def get_batch(batch_id: str, user: dict = Depends(get_current_user)):
    batch = _batches.get(batch_id)
    if not batch or batch["account_id"] != str(user["account_id"]):
        raise HTTPException(404, "Batch not found")
    return batch


@router.post("/{batch_id}/poll")
async def poll_batch(
    batch_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Poll all sub-jobs, collect results, deduplicate leads."""
    batch = _batches.get(batch_id)
    if not batch or batch["account_id"] != str(user["account_id"]):
        raise HTTPException(404, "Batch not found")

    if batch["status"] == "completed":
        return {
            "status": "completed",
            "total_leads_created": batch["total_leads_created"],
            "completed": batch["completed"],
            "total_searches": batch["total_searches"],
        }

    account_id = uuid.UUID(batch["account_id"])

    # Get or create default pipeline
    pipelines = pipe_crud.list_pipelines(db, account_id)
    if pipelines:
        pipeline = pipelines[0]
    else:
        pipeline = pipe_crud.create_pipeline(db, account_id, "Default Pipeline")
    default_stage = pipe_crud.get_default_stage(db, pipeline.id)

    # Track seen items for deduplication across sub-jobs
    seen_phones: set[str] = set()
    seen_urls: set[str] = set()
    total_new = 0

    async def _process_job(job):
        nonlocal total_new
        if job["status"] in ("completed", "error"):
            return

        # Check Apify status
        try:
            run_data = await apify_svc.get_run_status(job["apify_run_id"])
        except Exception:
            return

        apify_status = run_data.get("status", "RUNNING")
        if apify_status not in ("SUCCEEDED",):
            return

        # Fetch dataset
        try:
            items = await apify_svc.get_dataset_items(job["dataset_id"], limit=job["max_items"])
        except Exception:
            job["status"] = "error"
            return

        # Normalize and deduplicate
        normalized = []
        for item in items:
            n = apify_svc.normalize_place(item)
            phone = n.get("phone") or ""
            gmap_url = n.get("google_maps_url") or ""

            if (phone and phone in seen_phones) or (gmap_url and gmap_url in seen_urls):
                continue

            if phone: seen_phones.add(phone)
            if gmap_url: seen_urls.add(gmap_url)

            n["icp_score"] = compute_icp_score(
                industry=n.get("industry"),
                city=n.get("city"),
                website=n.get("website"),
                phone=n.get("phone"),
            )
            normalized.append(n)

        source_id = uuid.UUID(job["source_id"])
        leads = leads_crud.bulk_create_leads(
            db, account_id, normalized,
            source_id=source_id,
            pipeline_id=pipeline.id,
            stage_id=default_stage.id if default_stage else None,
        )

        job["status"] = "completed"
        job["leads_created"] = len(leads)
        batch["completed"] += 1
        total_new += len(leads)

    # Parallelize job processing
    await asyncio.gather(*[_process_job(j) for j in batch["sub_jobs"]])

    batch["total_leads_created"] += total_new

    if batch["completed"] >= batch["total_searches"]:
        batch["status"] = "completed"

    return {
        "status": batch["status"],
        "total_leads_created": batch["total_leads_created"],
        "completed": batch["completed"],
        "total_searches": batch["total_searches"],
    }
