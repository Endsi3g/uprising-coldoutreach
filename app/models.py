"""SQLAlchemy ORM models — 12 tables."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


def _uuid():
    return uuid.uuid4()


# ── helpers for sqlite test compat ──────────────────────────────────────────
# We use String(36) fallback when ARRAY/JSONB are unavailable (tests on sqlite).
# The column definitions below use generic types with postgresql variants.


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Uuid, primary_key=True, default=_uuid)
    name = Column(String(255), nullable=False)
    time_zone = Column(String(64), default="America/Montreal")
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    users = relationship("User", back_populates="account", cascade="all, delete-orphan")
    pipelines = relationship("Pipeline", back_populates="account", cascade="all, delete-orphan")
    lead_sources = relationship("LeadSource", back_populates="account", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="account", cascade="all, delete-orphan")
    outbound_identities = relationship("OutboundIdentity", back_populates="account", cascade="all, delete-orphan")
    sequences = relationship("Sequence", back_populates="account", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="account", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="account", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=_uuid)
    account_id = Column(Uuid, ForeignKey("accounts.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(16), default="admin")
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    account = relationship("Account", back_populates="users")


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(Uuid, primary_key=True, default=_uuid)
    account_id = Column(Uuid, ForeignKey("accounts.id"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    account = relationship("Account", back_populates="pipelines")
    stages = relationship("PipelineStage", back_populates="pipeline", cascade="all, delete-orphan",
                          order_by="PipelineStage.order_index")
    leads = relationship("Lead", back_populates="pipeline")


class PipelineStage(Base):
    __tablename__ = "pipeline_stages"

    id = Column(Uuid, primary_key=True, default=_uuid)
    pipeline_id = Column(Uuid, ForeignKey("pipelines.id"), nullable=False)
    name = Column(String(64), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    color = Column(String(7), nullable=True)

    pipeline = relationship("Pipeline", back_populates="stages")
    leads = relationship("Lead", back_populates="stage")


class LeadSource(Base):
    __tablename__ = "lead_sources"

    id = Column(Uuid, primary_key=True, default=_uuid)
    account_id = Column(Uuid, ForeignKey("accounts.id"), nullable=False)
    type = Column(String(32), nullable=False)  # google_maps | manual | csv_import
    metadata_ = Column("metadata", JSON, default=dict)
    leads_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    account = relationship("Account", back_populates="lead_sources")
    leads = relationship("Lead", back_populates="source")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Uuid, primary_key=True, default=_uuid)
    account_id = Column(Uuid, ForeignKey("accounts.id"), nullable=False)
    pipeline_id = Column(Uuid, ForeignKey("pipelines.id"), nullable=True)
    stage_id = Column(Uuid, ForeignKey("pipeline_stages.id"), nullable=True)
    source_id = Column(Uuid, ForeignKey("lead_sources.id"), nullable=True)

    company_name = Column(String(512), nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(64), nullable=True)
    website = Column(String(512), nullable=True)
    google_maps_url = Column(String(1024), nullable=True)
    address = Column(String(512), nullable=True)
    city = Column(String(128), nullable=True)
    country = Column(String(64), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    industry = Column(String(255), nullable=True)
    tags = Column(JSON, default=list)
    icp_score = Column(Integer, default=0)
    heat_score = Column(Integer, default=0)
    status = Column(String(32), default="active")

    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    account = relationship("Account", back_populates="leads")
    pipeline = relationship("Pipeline", back_populates="leads")
    stage = relationship("PipelineStage", back_populates="leads")
    source = relationship("LeadSource", back_populates="leads")
    activities = relationship("Activity", back_populates="lead", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="lead", cascade="all, delete-orphan")
    enrollments = relationship("SequenceEnrollment", back_populates="lead", cascade="all, delete-orphan")


class OutboundIdentity(Base):
    __tablename__ = "outbound_identities"

    id = Column(Uuid, primary_key=True, default=_uuid)
    account_id = Column(Uuid, ForeignKey("accounts.id"), nullable=False)
    type = Column(String(32), nullable=False)  # email_smtp | sms | instagram_dm | linkedin_dm
    label = Column(String(128), nullable=False)
    config = Column(JSON, default=dict)
    is_default = Column(Boolean, default=False)
    daily_limit = Column(Integer, default=500)
    used_today = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    account = relationship("Account", back_populates="outbound_identities")


class Sequence(Base):
    __tablename__ = "sequences"

    id = Column(Uuid, primary_key=True, default=_uuid)
    account_id = Column(Uuid, ForeignKey("accounts.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    account = relationship("Account", back_populates="sequences")
    steps = relationship("SequenceStep", back_populates="sequence", cascade="all, delete-orphan",
                         order_by="SequenceStep.order_index")
    enrollments = relationship("SequenceEnrollment", back_populates="sequence", cascade="all, delete-orphan")


class SequenceStep(Base):
    __tablename__ = "sequence_steps"

    id = Column(Uuid, primary_key=True, default=_uuid)
    sequence_id = Column(Uuid, ForeignKey("sequences.id"), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    type = Column(String(32), nullable=False)  # email | sms | dm | wait | condition
    channel_identity_id = Column(Uuid, ForeignKey("outbound_identities.id"), nullable=True)
    wait_hours = Column(Integer, nullable=True)
    template_subject = Column(String(512), nullable=True)
    template_body = Column(Text, nullable=True)
    condition_type = Column(String(64), nullable=True)
    condition_params = Column(JSON, nullable=True)
    # A/B testing
    variant_b_subject = Column(String(512), nullable=True)
    variant_b_body = Column(Text, nullable=True)
    ab_split_pct = Column(Integer, default=50)  # % of leads that get variant B
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    sequence = relationship("Sequence", back_populates="steps")
    channel_identity = relationship("OutboundIdentity")


class SequenceEnrollment(Base):
    __tablename__ = "sequence_enrollments"

    id = Column(Uuid, primary_key=True, default=_uuid)
    sequence_id = Column(Uuid, ForeignKey("sequences.id"), nullable=False)
    lead_id = Column(Uuid, ForeignKey("leads.id"), nullable=False)
    status = Column(String(32), default="pending")  # pending|running|paused|completed|cancelled
    current_step_index = Column(Integer, default=0)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    sequence = relationship("Sequence", back_populates="enrollments")
    lead = relationship("Lead", back_populates="enrollments")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Uuid, primary_key=True, default=_uuid)
    account_id = Column(Uuid, ForeignKey("accounts.id"), nullable=False)
    lead_id = Column(Uuid, ForeignKey("leads.id"), nullable=False)
    type = Column(String(64), nullable=False)
    data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    account = relationship("Account", back_populates="activities")
    lead = relationship("Lead", back_populates="activities")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Uuid, primary_key=True, default=_uuid)
    account_id = Column(Uuid, ForeignKey("accounts.id"), nullable=False)
    lead_id = Column(Uuid, ForeignKey("leads.id"), nullable=False)
    direction = Column(String(16), nullable=False, default="outbound")
    channel = Column(String(16), nullable=False, default="email")
    from_identity_id = Column(Uuid, ForeignKey("outbound_identities.id"), nullable=True)
    to_email = Column(String(255), nullable=True)
    to_phone = Column(String(64), nullable=True)
    subject = Column(String(512), nullable=True)
    body_html = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    provider_message_id = Column(String(255), nullable=True)
    status = Column(String(32), default="queued")
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    account = relationship("Account", back_populates="messages")
    lead = relationship("Lead", back_populates="messages")
    from_identity = relationship("OutboundIdentity")
