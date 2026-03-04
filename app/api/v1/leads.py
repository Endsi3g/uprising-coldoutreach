"""Lead endpoints – CRUD, stage moves, sequence enrollment, CSV import/export."""

from __future__ import annotations

import csv
import io
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import leads as leads_crud
from app.crud import sequences as seq_crud
from app.schemas import LeadCreate, LeadOut, LeadUpdate

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("", response_model=list[LeadOut])
def list_leads(
    pipeline_id: uuid.UUID | None = None,
    stage_id: uuid.UUID | None = None,
    city: str | None = None,
    icp_score_gte: int | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return leads_crud.list_leads(
        db, user["account_id"],
        pipeline_id=pipeline_id,
        stage_id=stage_id,
        city=city,
        icp_score_gte=icp_score_gte,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: uuid.UUID, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    lead = leads_crud.get_lead(db, lead_id)
    if not lead or lead.account_id != user["account_id"]:
        raise HTTPException(404, "Lead not found")
    return lead


@router.post("", response_model=LeadOut, status_code=201)
def create_lead(body: LeadCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return leads_crud.create_lead(db, user["account_id"], **body.model_dump())


@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: uuid.UUID,
    body: LeadUpdate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = leads_crud.get_lead(db, lead_id)
    if not lead or lead.account_id != user["account_id"]:
        raise HTTPException(404, "Lead not found")
    return leads_crud.update_lead(db, lead, body.model_dump(exclude_unset=True))


@router.post("/{lead_id}/move-stage", response_model=LeadOut)
def move_stage(
    lead_id: uuid.UUID,
    stage_id: uuid.UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = leads_crud.get_lead(db, lead_id)
    if not lead or lead.account_id != user["account_id"]:
        raise HTTPException(404, "Lead not found")
    return leads_crud.move_stage(db, lead, stage_id, user["account_id"])


@router.post("/{lead_id}/enroll-sequence/{seq_id}", status_code=201)
def enroll_lead(
    lead_id: uuid.UUID,
    seq_id: uuid.UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = leads_crud.get_lead(db, lead_id)
    if not lead or lead.account_id != user["account_id"]:
        raise HTTPException(404, "Lead not found")
    enrollment = seq_crud.create_enrollment(db, seq_id, lead_id, start_immediately=True)
    return {"id": str(enrollment.id), "status": enrollment.status}


# ── CSV Import / Export ─────────────────────────────────────────────────────

CSV_LEAD_FIELDS = [
    "company_name", "first_name", "last_name", "email", "phone",
    "website", "address", "city", "country", "industry", "tags",
]


@router.post("/csv-import", status_code=201)
async def csv_import(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a CSV file to bulk-import leads."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only .csv files are accepted")

    content = await file.read()
    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))

    created = 0
    skipped = 0
    errors = []

    for i, row in enumerate(reader, start=2):  # row 1 = header
        company = (row.get("company_name") or row.get("company") or "").strip()
        if not company:
            errors.append(f"Row {i}: missing company_name, skipped")
            skipped += 1
            continue

        lead_data = {
            "company_name": company,
            "first_name": (row.get("first_name") or "").strip() or None,
            "last_name": (row.get("last_name") or "").strip() or None,
            "email": (row.get("email") or "").strip() or None,
            "phone": (row.get("phone") or "").strip() or None,
            "website": (row.get("website") or "").strip() or None,
            "address": (row.get("address") or "").strip() or None,
            "city": (row.get("city") or "").strip() or None,
            "country": (row.get("country") or "").strip() or None,
            "industry": (row.get("industry") or "").strip() or None,
            "tags": [t.strip() for t in (row.get("tags") or "").split(",") if t.strip()],
        }
        try:
            leads_crud.create_lead(db, user["account_id"], **lead_data)
            created += 1
        except Exception as e:
            errors.append(f"Row {i}: {e}")
            skipped += 1

    return {"leads_created": created, "leads_skipped": skipped, "errors": errors[:20]}


@router.get("/csv-export")
def csv_export(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download all leads as a CSV file."""
    all_leads = leads_crud.list_leads(db, user["account_id"], limit=10000)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_LEAD_FIELDS + ["icp_score", "heat_score", "status"])
    writer.writeheader()

    for lead in all_leads:
        writer.writerow({
            "company_name": lead.company_name or "",
            "first_name": lead.first_name or "",
            "last_name": lead.last_name or "",
            "email": lead.email or "",
            "phone": lead.phone or "",
            "website": lead.website or "",
            "address": lead.address or "",
            "city": lead.city or "",
            "country": lead.country or "",
            "industry": lead.industry or "",
            "tags": ",".join(lead.tags or []),
            "icp_score": lead.icp_score,
            "heat_score": lead.heat_score,
            "status": lead.status or "",
        })

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"},
    )

