"""Pydantic request / response schemas for every model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


# ── helpers ─────────────────────────────────────────────────────────────────

class _Base(BaseModel):
    model_config = {"from_attributes": True}


# ── Auth ────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ── Account ─────────────────────────────────────────────────────────────────

class AccountCreate(BaseModel):
    name: str
    time_zone: str = "America/Montreal"


class AccountOut(_Base):
    id: uuid.UUID
    name: str
    time_zone: str
    created_at: datetime


# ── User ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "admin"


class UserOut(_Base):
    id: uuid.UUID
    account_id: uuid.UUID
    email: str
    role: str
    created_at: datetime


# ── Pipeline ────────────────────────────────────────────────────────────────

class PipelineCreate(BaseModel):
    name: str


class PipelineOut(_Base):
    id: uuid.UUID
    account_id: uuid.UUID
    name: str
    created_at: datetime


class PipelineStageCreate(BaseModel):
    name: str
    order_index: int = 0
    color: str | None = None


class PipelineStageOut(_Base):
    id: uuid.UUID
    pipeline_id: uuid.UUID
    name: str
    order_index: int
    color: str | None


# ── LeadSource ──────────────────────────────────────────────────────────────

class LeadSourceOut(_Base):
    id: uuid.UUID
    account_id: uuid.UUID
    type: str
    metadata_: dict[str, Any] | None = Field(None, alias="metadata_")
    leads_count: int
    created_at: datetime


# ── Lead ────────────────────────────────────────────────────────────────────

class LeadCreate(BaseModel):
    company_name: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    google_maps_url: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    lat: float | None = None
    lng: float | None = None
    industry: str | None = None
    tags: list[str] = []
    pipeline_id: uuid.UUID | None = None
    stage_id: uuid.UUID | None = None


class LeadUpdate(BaseModel):
    company_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    industry: str | None = None
    tags: list[str] | None = None
    status: str | None = None
    stage_id: uuid.UUID | None = None


class LeadOut(_Base):
    id: uuid.UUID
    account_id: uuid.UUID
    pipeline_id: uuid.UUID | None
    stage_id: uuid.UUID | None
    source_id: uuid.UUID | None
    company_name: str
    first_name: str | None
    last_name: str | None
    email: str | None
    phone: str | None
    website: str | None
    google_maps_url: str | None
    address: str | None
    city: str | None
    country: str | None
    lat: float | None
    lng: float | None
    industry: str | None
    tags: list[str] | None
    icp_score: int
    heat_score: int
    status: str
    created_at: datetime
    updated_at: datetime


# ── OutboundIdentity ────────────────────────────────────────────────────────

class OutboundIdentityCreate(BaseModel):
    type: str
    label: str
    config: dict[str, Any] = {}
    is_default: bool = False
    daily_limit: int = 500


class OutboundIdentityOut(_Base):
    id: uuid.UUID
    account_id: uuid.UUID
    type: str
    label: str
    config: dict[str, Any]
    is_default: bool
    daily_limit: int
    used_today: int
    created_at: datetime


# ── Sequence ────────────────────────────────────────────────────────────────

class SequenceCreate(BaseModel):
    name: str
    description: str | None = None


class SequenceOut(_Base):
    id: uuid.UUID
    account_id: uuid.UUID
    name: str
    description: str | None
    is_active: bool
    created_at: datetime


class SequenceStepCreate(BaseModel):
    order_index: int
    type: str  # email | sms | dm | wait | condition
    channel_identity_id: uuid.UUID | None = None
    wait_hours: int | None = None
    template_subject: str | None = None
    template_body: str | None = None
    condition_type: str | None = None
    condition_params: dict[str, Any] | None = None


class SequenceStepOut(_Base):
    id: uuid.UUID
    sequence_id: uuid.UUID
    order_index: int
    type: str
    channel_identity_id: uuid.UUID | None
    wait_hours: int | None
    template_subject: str | None
    template_body: str | None
    condition_type: str | None
    condition_params: dict[str, Any] | None
    created_at: datetime


# ── Enrollment ──────────────────────────────────────────────────────────────

class EnrollmentBulkRequest(BaseModel):
    lead_ids: list[uuid.UUID]
    start_immediately: bool = True


class EnrollmentOut(_Base):
    id: uuid.UUID
    sequence_id: uuid.UUID
    lead_id: uuid.UUID
    status: str
    current_step_index: int
    next_run_at: datetime | None
    created_at: datetime


# ── Messages ────────────────────────────────────────────────────────────────

class MessageSendRequest(BaseModel):
    identity_id: uuid.UUID
    lead_id: uuid.UUID
    to_email: str
    subject: str
    body_html: str
    tracking_pixel: bool = True
    track_clicks: bool = True


class MessageOut(_Base):
    id: uuid.UUID
    account_id: uuid.UUID
    lead_id: uuid.UUID
    direction: str
    channel: str
    to_email: str | None
    to_phone: str | None
    subject: str | None
    body_html: str | None
    body_text: str | None
    status: str
    created_at: datetime


# ── Google Maps Job ─────────────────────────────────────────────────────────

class GoogleMapsJobRequest(BaseModel):
    query: str
    location: str
    max_items: int = 200
    radius_km: int = 20


class GoogleMapsJobOut(_Base):
    id: uuid.UUID
    account_id: uuid.UUID
    status: str
    query: str
    location: str
    max_items: int
    leads_created: int
    created_at: datetime


# ── Activity ────────────────────────────────────────────────────────────────

class ActivityOut(_Base):
    id: uuid.UUID
    account_id: uuid.UUID
    lead_id: uuid.UUID
    type: str
    data: dict[str, Any] | None
    created_at: datetime


# ── Analytics ───────────────────────────────────────────────────────────────

class AnalyticsOverview(BaseModel):
    total_leads: int = 0
    active_sequences: int = 0
    emails_sent_today: int = 0
    open_rate: float = 0.0
    reply_rate: float = 0.0


class PipelineFunnelStage(BaseModel):
    stage_name: str
    count: int
    color: str | None = None


class PipelineFunnel(BaseModel):
    pipeline_name: str
    stages: list[PipelineFunnelStage] = []


# ── Multi-Search ────────────────────────────────────────────────────────────

class MultiSearchItemRequest(BaseModel):
    query: str
    location: str
    max_items: int = 200
    radius_km: int = 20


class MultiSearchRequest(BaseModel):
    searches: list[MultiSearchItemRequest]


class MultiSearchBatchOut(BaseModel):
    batch_id: str
    total_searches: int
    status: str
    sub_jobs_started: int = 0


# ── CSV Import/Export ───────────────────────────────────────────────────────

class CsvImportResponse(BaseModel):
    leads_created: int = 0
    leads_skipped: int = 0
    errors: list[str] = []


# ── Webhook ─────────────────────────────────────────────────────────────────

class WebhookReplyPayload(BaseModel):
    from_email: str
    subject: str = ""
    body_text: str = ""
    provider_message_id: str | None = None
    signature: str | None = None

