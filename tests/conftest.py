"""Pytest fixtures — in-memory SQLite DB, TestClient, seed data."""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models import (
    Account,
    Lead,
    OutboundIdentity,
    Pipeline,
    PipelineStage,
    Sequence,
    SequenceStep,
    User,
)

# ── In-memory SQLite engine ────────────────────────────────────────────────
# StaticPool ensures all connections share the same in-memory DB so that
# tables created in the test session are visible inside FastAPI endpoints.

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Enable FK enforcement in SQLite
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def db_session():
    """Create tables fresh for every test, yield session, then drop."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with DB override."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def seed_account(db_session):
    account = Account(id=uuid.uuid4(), name="Test Co", time_zone="UTC")
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


@pytest.fixture
def seed_user(db_session, seed_account):
    user = User(
        id=uuid.uuid4(),
        account_id=seed_account.id,
        email="test@example.com",
        hashed_password=hash_password("password123"),
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(seed_user, seed_account):
    token = create_access_token({
        "sub": str(seed_user.id),
        "account_id": str(seed_account.id),
        "role": "admin",
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seed_pipeline(db_session, seed_account):
    pipeline = Pipeline(id=uuid.uuid4(), account_id=seed_account.id, name="Test Pipeline")
    db_session.add(pipeline)
    db_session.flush()
    stages_data = [
        ("New", 0, "#6B7280"),
        ("Contacted", 1, "#3B82F6"),
        ("Hot", 2, "#EF4444"),
    ]
    stages = []
    for name, order, color in stages_data:
        s = PipelineStage(id=uuid.uuid4(), pipeline_id=pipeline.id, name=name, order_index=order, color=color)
        db_session.add(s)
        stages.append(s)
    db_session.commit()
    db_session.refresh(pipeline)
    return pipeline, stages


@pytest.fixture
def seed_lead(db_session, seed_account, seed_pipeline):
    pipeline, stages = seed_pipeline
    lead = Lead(
        id=uuid.uuid4(),
        account_id=seed_account.id,
        pipeline_id=pipeline.id,
        stage_id=stages[0].id,
        company_name="Plomberie Laval",
        email="contact@plomberie-laval.ca",
        phone="+15141234567",
        city="Laval",
        industry="plumber",
        icp_score=75,
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


@pytest.fixture
def seed_identity(db_session, seed_account):
    identity = OutboundIdentity(
        id=uuid.uuid4(),
        account_id=seed_account.id,
        type="email_smtp",
        label="Test Gmail",
        config={
            "host": "smtp.gmail.com",
            "port": 465,
            "username": "test@gmail.com",
            "app_password": "abcd efgh ijkl mnop",
            "from_name": "Test",
            "from_email": "test@gmail.com",
        },
        is_default=True,
        daily_limit=500,
        used_today=0,
    )
    db_session.add(identity)
    db_session.commit()
    db_session.refresh(identity)
    return identity


@pytest.fixture
def seed_sequence(db_session, seed_account, seed_identity):
    seq = Sequence(id=uuid.uuid4(), account_id=seed_account.id, name="Test Sequence")
    db_session.add(seq)
    db_session.flush()
    steps = [
        SequenceStep(
            id=uuid.uuid4(), sequence_id=seq.id, order_index=0, type="email",
            channel_identity_id=seed_identity.id,
            template_subject="Hi {{first_name}}",
            template_body="<p>Hello {{first_name}} from {{company_name}}!</p>",
        ),
        SequenceStep(
            id=uuid.uuid4(), sequence_id=seq.id, order_index=1, type="wait",
            wait_hours=24,
        ),
        SequenceStep(
            id=uuid.uuid4(), sequence_id=seq.id, order_index=2, type="email",
            channel_identity_id=seed_identity.id,
            template_subject="Follow up — {{company_name}}",
            template_body="<p>Just checking in, {{first_name}}.</p>",
        ),
    ]
    for s in steps:
        db_session.add(s)
    db_session.commit()
    db_session.refresh(seq)
    return seq, steps
