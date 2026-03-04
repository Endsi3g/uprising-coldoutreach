"""Test SQLAlchemy models — relationships, defaults, constraints."""

import uuid

from app.models import Account, Lead, Pipeline, PipelineStage, User


def test_account_creation(db_session):
    account = Account(name="ACME Corp", time_zone="America/Montreal")
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    assert account.id is not None
    assert account.name == "ACME Corp"
    assert account.time_zone == "America/Montreal"
    assert account.created_at is not None


def test_user_account_relationship(db_session, seed_account, seed_user):
    user = seed_user
    assert user.account_id == seed_account.id
    assert user.role == "admin"
    assert user.hashed_password != "password123"


def test_pipeline_stage_ordering(db_session, seed_pipeline):
    pipeline, stages = seed_pipeline
    assert len(stages) == 3
    assert stages[0].name == "New"
    assert stages[0].order_index == 0
    assert stages[2].name == "Hot"
    assert stages[2].order_index == 2


def test_lead_defaults(db_session, seed_lead):
    lead = seed_lead
    assert lead.icp_score == 75
    assert lead.heat_score == 0
    assert lead.status == "active"
    assert lead.company_name == "Plomberie Laval"


def test_lead_pipeline_relationship(db_session, seed_lead, seed_pipeline):
    pipeline, stages = seed_pipeline
    assert seed_lead.pipeline_id == pipeline.id
    assert seed_lead.stage_id == stages[0].id


def test_uuid_primary_keys(db_session, seed_account):
    assert isinstance(seed_account.id, uuid.UUID)
