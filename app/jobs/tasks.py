"""Celery background tasks for email sending and Apify polling."""

from __future__ import annotations

import uuid

from app.core.database import SessionLocal
from app.crud import messages as msg_crud
from app.jobs.celery_app import celery_app
from app.models import OutboundIdentity
from app.services.email import prepare_html, send_smtp_email


@celery_app.task(name="send_email_task", bind=True, max_retries=3)
def send_email_task(self, message_id: str, identity_id: str):
    """Send a single email via SMTP in background."""
    db = SessionLocal()
    try:
        msg = msg_crud.get_message(db, uuid.UUID(message_id))
        if not msg:
            return {"error": "Message not found"}

        identity = db.get(OutboundIdentity, uuid.UUID(identity_id))
        if not identity:
            return {"error": "Identity not found"}

        if identity.used_today >= identity.daily_limit:
            msg_crud.update_message_status(db, msg, "failed")
            return {"error": "Daily limit reached"}

        # Prepare email with tracking
        final_html = prepare_html(
            msg.body_html or "",
            msg.id,
            add_pixel=True,
            track_clicks=True,
        )

        success = send_smtp_email(
            identity.config,
            msg.to_email,
            msg.subject or "",
            final_html,
        )

        if success:
            msg_crud.update_message_status(db, msg, "sent")
            identity.used_today += 1
            db.commit()
            msg_crud.record_activity(
                db, msg.account_id, msg.lead_id, "email_sent",
                {"message_id": message_id},
            )
            return {"status": "sent"}
        else:
            msg_crud.update_message_status(db, msg, "failed")
            return {"status": "failed"}
    except Exception as exc:
        msg_crud.update_message_status(db, msg_crud.get_message(db, uuid.UUID(message_id)), "failed")
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()


@celery_app.task(name="poll_apify_job_task")
def poll_apify_job_task(run_id: str, dataset_id: str, account_id: str, source_id: str):
    """Poll Apify run and create leads when done (used by scheduler)."""
    from app.crud import leads as leads_crud
    from app.crud import pipelines as pipe_crud
    from app.services import apify as apify_svc
    from app.services.scoring import compute_icp_score

    db = SessionLocal()
    import asyncio
    try:
        run_data = asyncio.run(apify_svc.get_run_status(run_id))
        if run_data.get("status") != "SUCCEEDED":
            return {"status": run_data.get("status")}

        items = asyncio.run(apify_svc.get_dataset_items(dataset_id))
        aid = uuid.UUID(account_id)
        sid = uuid.UUID(source_id)

        pipelines = pipe_crud.list_pipelines(db, aid)
        pipeline = pipelines[0] if pipelines else pipe_crud.create_pipeline(db, aid, "Default Pipeline")
        default_stage = pipe_crud.get_default_stage(db, pipeline.id)

        normalized = [apify_svc.normalize_place(item) for item in items]
        for n in normalized:
            n["icp_score"] = compute_icp_score(
                industry=n.get("industry"),
                city=n.get("city"),
                website=n.get("website"),
                phone=n.get("phone"),
            )

        leads = leads_crud.bulk_create_leads(
            db, aid, normalized,
            source_id=sid,
            pipeline_id=pipeline.id,
            stage_id=default_stage.id if default_stage else None,
        )
        return {"status": "completed", "leads_created": len(leads)}
    finally:
        db.close()
