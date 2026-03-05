"""Sequence engine scheduler — processes due enrollments every 2 minutes.

Handles: email, sms (TextBelt), dm (Instagram), wait, condition steps.
Also runs IMAP reply detection and daily counter reset.
"""

from __future__ import annotations

import logging
import random
import time

from apscheduler.schedulers.blocking import BlockingScheduler

from app.core.database import SessionLocal
from app.crud import messages as msg_crud
from app.crud import sequences as seq_crud
from app.models import Lead, Message, OutboundIdentity, SequenceEnrollment, SequenceStep
from app.services.email import prepare_html, render_template, send_smtp_email
from app.services.sms import send_sms
from app.services.instagram import send_dm as send_ig_dm
from app.services.gmail import send_gmail_api, refresh_access_token
from app.services import imap as imap_svc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scheduler")


def process_due_enrollments():
    """Main sequence engine loop: process all due enrollments."""
    db = SessionLocal()
    try:
        enrollments = seq_crud.get_due_enrollments(db)
        logger.info(f"Processing {len(enrollments)} due enrollments")

        for enrollment in enrollments:
            try:
                _process_single_enrollment(db, enrollment)
            except Exception as e:
                logger.error(f"Error processing enrollment {enrollment.id}: {e}")
    finally:
        db.close()


def _process_single_enrollment(db, enrollment):
    """Process a single enrollment: execute current step, advance to next."""
    steps = seq_crud.list_steps(db, enrollment.sequence_id)
    if not steps or enrollment.current_step_index >= len(steps):
        seq_crud.complete_enrollment(db, enrollment)
        return

    step = steps[enrollment.current_step_index]
    lead = db.get(Lead, enrollment.lead_id)
    if not lead:
        seq_crud.complete_enrollment(db, enrollment)
        return

    if step.type == "wait":
        # Just advance to next step after wait_hours
        next_idx = enrollment.current_step_index + 1
        if next_idx >= len(steps):
            seq_crud.complete_enrollment(db, enrollment)
        else:
            next_step = steps[next_idx]
            wait = next_step.wait_hours or 0
            seq_crud.advance_enrollment(db, enrollment, next_idx, wait_hours=wait)

    elif step.type == "email":
        _execute_email_step(db, step, lead, enrollment, steps)

    elif step.type == "sms":
        _execute_sms_step(db, step, lead, enrollment, steps)

    elif step.type == "dm":
        _execute_dm_step(db, step, lead, enrollment, steps)

    elif step.type == "condition":
        _evaluate_condition(db, step, lead, enrollment, steps)

    else:
        logger.info(f"Step type '{step.type}' not yet implemented, skipping")
        _advance_to_next(db, enrollment, steps)


def _select_ab_variant(step: SequenceStep) -> tuple[str, str, str]:
    """Select A/B test variant. Returns (subject, body, variant_label)."""
    has_variant_b = step.variant_b_subject or step.variant_b_body
    if not has_variant_b:
        return (step.template_subject or "", step.template_body or "", "A")

    split_pct = step.ab_split_pct or 50
    if random.randint(1, 100) <= split_pct:
        return (
            step.variant_b_subject or step.template_subject or "",
            step.variant_b_body or step.template_body or "",
            "B",
        )
    return (step.template_subject or "", step.template_body or "", "A")


def _find_identity(db, step, lead, identity_type: str):
    """Find outbound identity for a step."""
    identity = None
    if step.channel_identity_id:
        identity = db.get(OutboundIdentity, step.channel_identity_id)
    if not identity:
        identity = (
            db.query(OutboundIdentity)
            .filter(
                OutboundIdentity.account_id == lead.account_id,
                OutboundIdentity.type == identity_type,
                OutboundIdentity.is_default.is_(True),
            )
            .first()
        )
    if not identity:
        # Try any identity of this type
        identity = (
            db.query(OutboundIdentity)
            .filter(
                OutboundIdentity.account_id == lead.account_id,
                OutboundIdentity.type == identity_type,
            )
            .first()
        )
    return identity


def _execute_email_step(db, step: SequenceStep, lead: Lead, enrollment, steps):
    """Send email for an email step (SMTP or Gmail API)."""
    if not lead.email:
        logger.warning(f"Lead {lead.id} has no email, skipping")
        _advance_to_next(db, enrollment, steps)
        return

    # Try gmail_api identity first, then email_smtp
    identity = _find_identity(db, step, lead, "gmail_api")
    if not identity:
        identity = _find_identity(db, step, lead, "email_smtp")
    if not identity:
        logger.error(f"No email identity found for account {lead.account_id}")
        _advance_to_next(db, enrollment, steps)
        return

    # Check daily limit
    if identity.used_today >= identity.daily_limit:
        logger.warning(f"Daily limit reached for identity {identity.id}")
        return  # will retry next cycle

    # A/B variant selection
    subject_tmpl, body_tmpl, variant = _select_ab_variant(step)

    # Render template
    lead_data = {
        "first_name": lead.first_name or "",
        "last_name": lead.last_name or "",
        "company_name": lead.company_name or "",
        "email": lead.email or "",
        "city": lead.city or "",
        "industry": lead.industry or "",
    }
    subject = render_template(subject_tmpl, lead_data)
    body = render_template(body_tmpl, lead_data)

    # Create message record
    msg = msg_crud.create_message(
        db,
        account_id=lead.account_id,
        lead_id=lead.id,
        direction="outbound",
        channel="email",
        from_identity_id=identity.id,
        to_email=lead.email,
        subject=subject,
        body_html=body,
        status="queued",
    )

    # Prepare and send
    final_html = prepare_html(body, msg.id)

    if identity.type == "gmail_api":
        # Send via Gmail API
        access_token = identity.config.get("access_token", "")
        refresh_tok = identity.config.get("refresh_token", "")
        from_email = identity.config.get("from_email", "")
        from_name = identity.config.get("from_name", "")

        # Try to refresh token if needed
        try:
            new_tokens = refresh_access_token(refresh_tok)
            access_token = new_tokens.get("access_token", access_token)
            identity.config = {**identity.config, "access_token": access_token}
            db.commit()
        except Exception:
            pass  # Use existing token

        result = send_gmail_api(access_token, lead.email, subject, final_html, from_email, from_name)
        success = "id" in result and "error" not in result
    else:
        # Send via SMTP
        success = send_smtp_email(identity.config, lead.email, subject, final_html)

    if success:
        msg_crud.update_message_status(db, msg, "sent")
        identity.used_today += 1
        db.commit()
        msg_crud.record_activity(
            db, lead.account_id, lead.id, "email_sent",
            {
                "message_id": str(msg.id),
                "sequence_step": step.order_index,
                "variant": variant,
                "channel_type": identity.type,
            },
        )
        logger.info(f"Email sent to {lead.email} (step {step.order_index}, variant {variant})")
    else:
        msg_crud.update_message_status(db, msg, "failed")
        logger.error(f"Email failed for {lead.email}")

    _advance_to_next(db, enrollment, steps)


def _execute_sms_step(db, step: SequenceStep, lead: Lead, enrollment, steps):
    """Send SMS via TextBelt for an sms step."""
    if not lead.phone:
        logger.warning(f"Lead {lead.id} has no phone, skipping SMS")
        _advance_to_next(db, enrollment, steps)
        return

    identity = _find_identity(db, step, lead, "sms")

    # Check daily limit
    if identity and identity.used_today >= identity.daily_limit:
        logger.warning(f"Daily SMS limit reached for identity {identity.id}")
        return

    # Render template
    lead_data = {
        "first_name": lead.first_name or "",
        "last_name": lead.last_name or "",
        "company_name": lead.company_name or "",
        "phone": lead.phone or "",
        "city": lead.city or "",
    }
    message = render_template(step.template_body or "", lead_data)

    # Get API key from identity config or settings
    api_key = None
    if identity:
        api_key = identity.config.get("api_key")

    # Create message record
    msg = msg_crud.create_message(
        db,
        account_id=lead.account_id,
        lead_id=lead.id,
        direction="outbound",
        channel="sms",
        from_identity_id=identity.id if identity else None,
        to_email=None,
        to_phone=lead.phone,
        subject=None,
        body_html=None,
        body_text=message,
        status="queued",
    )

    result = send_sms(lead.phone, message, api_key=api_key)

    if result.get("success"):
        msg_crud.update_message_status(db, msg, "sent")
        if identity:
            identity.used_today += 1
        db.commit()
        msg_crud.record_activity(
            db, lead.account_id, lead.id, "sms_sent",
            {"message_id": str(msg.id), "sequence_step": step.order_index},
        )
        logger.info(f"SMS sent to {lead.phone} (step {step.order_index})")
    else:
        msg_crud.update_message_status(db, msg, "failed")
        logger.error(f"SMS failed for {lead.phone}: {result.get('error')}")

    _advance_to_next(db, enrollment, steps)


def _execute_dm_step(db, step: SequenceStep, lead: Lead, enrollment, steps):
    """Send DM via Instagram for a dm step."""
    identity = _find_identity(db, step, lead, "instagram_dm")
    if not identity:
        logger.warning(f"No Instagram DM identity found for account {lead.account_id}")
        _advance_to_next(db, enrollment, steps)
        return

    if identity.used_today >= identity.daily_limit:
        logger.warning(f"Daily DM limit reached for identity {identity.id}")
        return

    # Render template
    lead_data = {
        "first_name": lead.first_name or "",
        "last_name": lead.last_name or "",
        "company_name": lead.company_name or "",
        "city": lead.city or "",
    }
    message = render_template(step.template_body or "", lead_data)

    # Get the lead's IG scoped ID - stored in lead tags or a custom field
    # For now, we need the IG recipient ID to be stored somewhere on the lead
    recipient_id = None
    if lead.tags:
        for tag in lead.tags:
            if tag.startswith("ig:"):
                recipient_id = tag.replace("ig:", "")
                break

    if not recipient_id:
        logger.warning(f"Lead {lead.id} has no Instagram recipient ID, skipping DM")
        _advance_to_next(db, enrollment, steps)
        return

    access_token = identity.config.get("access_token", "")

    # Create message record
    msg = msg_crud.create_message(
        db,
        account_id=lead.account_id,
        lead_id=lead.id,
        direction="outbound",
        channel="instagram_dm",
        from_identity_id=identity.id,
        to_email=None,
        to_phone=None,
        subject=None,
        body_html=None,
        body_text=message,
        status="queued",
    )

    result = send_ig_dm(access_token, recipient_id, message)

    if "error" not in result:
        msg_crud.update_message_status(db, msg, "sent")
        identity.used_today += 1
        db.commit()
        msg_crud.record_activity(
            db, lead.account_id, lead.id, "dm_sent",
            {"message_id": str(msg.id), "sequence_step": step.order_index, "channel": "instagram"},
        )
        logger.info(f"Instagram DM sent to {recipient_id} (step {step.order_index})")
    else:
        msg_crud.update_message_status(db, msg, "failed")
        logger.error(f"Instagram DM failed: {result.get('error')}")

    _advance_to_next(db, enrollment, steps)


def _evaluate_condition(db, step: SequenceStep, lead: Lead, enrollment, steps):
    """Evaluate a condition step."""
    ctype = step.condition_type or ""

    if ctype == "if_reply":
        has_reply = (
            db.query(Message)
            .filter(Message.lead_id == lead.id, Message.direction == "inbound")
            .first()
        )
        if has_reply:
            seq_crud.complete_enrollment(db, enrollment)
            return

    elif ctype == "icp_score_gt_70":
        if lead.icp_score <= 70:
            seq_crud.complete_enrollment(db, enrollment)
            return

    # Default: continue
    _advance_to_next(db, enrollment, steps)


def _advance_to_next(db, enrollment, steps):
    """Advance enrollment to the next step."""
    next_idx = enrollment.current_step_index + 1
    if next_idx >= len(steps):
        seq_crud.complete_enrollment(db, enrollment)
    else:
        next_step = steps[next_idx]
        wait = next_step.wait_hours if next_step.type == "wait" else 0
        seq_crud.advance_enrollment(db, enrollment, next_idx, wait_hours=wait or 0)


# ── IMAP Reply Detection ───────────────────────────────────────────────────

def check_inbound_replies():
    """Check all SMTP identities for inbound replies via IMAP."""
    db = SessionLocal()
    try:
        identities = (
            db.query(OutboundIdentity)
            .filter(OutboundIdentity.type == "email_smtp")
            .all()
        )
        for identity in identities:
            config = identity.config or {}
            # Need IMAP config — derive from SMTP config
            imap_config = {
                "host": config.get("imap_host", config.get("host", "imap.gmail.com").replace("smtp.", "imap.")),
                "port": config.get("imap_port", 993),
                "username": config.get("username", ""),
                "password": config.get("app_password", ""),
            }
            if not imap_config["username"]:
                continue

            replies = imap_svc.check_for_replies(imap_config, since_hours=10)
            for reply in replies:
                from_email = reply.get("from_email", "")
                lead = (
                    db.query(Lead)
                    .filter(
                        Lead.account_id == identity.account_id,
                        Lead.email == from_email,
                    )
                    .first()
                )
                if not lead:
                    continue

                # Check if we already recorded this reply
                existing = (
                    db.query(Message)
                    .filter(
                        Message.lead_id == lead.id,
                        Message.direction == "inbound",
                        Message.provider_message_id == reply.get("message_id", ""),
                    )
                    .first()
                )
                if existing:
                    continue

                msg = msg_crud.create_message(
                    db,
                    account_id=lead.account_id,
                    lead_id=lead.id,
                    direction="inbound",
                    channel="email",
                    from_identity_id=None,
                    to_email=None,
                    subject=reply.get("subject", ""),
                    body_html=None,
                    body_text=reply.get("body_text", ""),
                    provider_message_id=reply.get("message_id", ""),
                    status="received",
                )
                lead.heat_score = min(100, lead.heat_score + 25)
                db.commit()

                msg_crud.record_activity(
                    db, lead.account_id, lead.id, "reply_received",
                    {"message_id": str(msg.id), "from_email": from_email},
                )

                # Pause active enrollments
                active = (
                    db.query(SequenceEnrollment)
                    .filter(
                        SequenceEnrollment.lead_id == lead.id,
                        SequenceEnrollment.status.in_(["pending", "running"]),
                    )
                    .all()
                )
                for enrollment in active:
                    enrollment.status = "paused"
                db.commit()

                logger.info(f"Inbound reply detected from {from_email} for lead {lead.id}")
    except Exception as e:
        logger.error(f"IMAP check error: {e}")
    finally:
        db.close()


# ── Daily Counter Reset ────────────────────────────────────────────────────

def reset_daily_counters():
    """Reset used_today counter for all outbound identities at midnight."""
    db = SessionLocal()
    try:
        db.query(OutboundIdentity).update({"used_today": 0})
        db.commit()
        logger.info("Daily counters reset for all outbound identities")
    finally:
        db.close()


# ── Scheduler entry point ──────────────────────────────────────────────────

def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(process_due_enrollments, "interval", minutes=2, id="sequence_engine")
    scheduler.add_job(check_inbound_replies, "interval", minutes=5, id="imap_checker")
    scheduler.add_job(reset_daily_counters, "cron", hour=0, minute=0, id="daily_reset")
    logger.info("Scheduler started: sequence engine (2min), IMAP checker (5min), daily reset (midnight)")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()


if __name__ == "__main__":
    main()

