"""IMAP reply detection — check inboxes for inbound replies from leads.

Periodically scans IMAP mailboxes configured on OutboundIdentities
and creates inbound Message records when replies are detected.
"""

from __future__ import annotations

import email
import imaplib
import logging
import re
from datetime import datetime, timedelta, timezone
from email.header import decode_header

logger = logging.getLogger("imap")


def _decode_header_value(value: str) -> str:
    """Decode an email header value (handles RFC 2047 encoding)."""
    parts = decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return " ".join(decoded)


def _extract_email_address(from_header: str) -> str:
    """Extract bare email address from 'Name <email>' format."""
    match = re.search(r"<([^>]+)>", from_header)
    if match:
        return match.group(1).lower()
    return from_header.strip().lower()


def check_for_replies(
    imap_config: dict,
    since_hours: int = 24,
) -> list[dict]:
    """Connect to IMAP and fetch unread emails from the last N hours.

    Expected imap_config keys:
      host, port (993), username, password, folder (INBOX)

    Returns list of dicts: {from_email, subject, body_text, date, message_id}
    """
    host = imap_config.get("host", "imap.gmail.com")
    port = int(imap_config.get("port", 993))
    username = imap_config["username"]
    password = imap_config.get("password") or imap_config.get("app_password", "")
    folder = imap_config.get("folder", "INBOX")

    since_date = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    date_str = since_date.strftime("%d-%b-%Y")

    results = []

    try:
        mail = imaplib.IMAP4_SSL(host, port)
        mail.login(username, password)
        mail.select(folder, readonly=True)

        # Search for unseen messages since date
        status, msg_ids = mail.search(None, f'(UNSEEN SINCE {date_str})')
        if status != "OK" or not msg_ids[0]:
            mail.logout()
            return results

        for msg_id in msg_ids[0].split():
            try:
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue

                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                from_header = _decode_header_value(msg.get("From", ""))
                from_email = _extract_email_address(from_header)
                subject = _decode_header_value(msg.get("Subject", ""))
                message_id = msg.get("Message-ID", "")

                # Extract body
                body_text = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        if ctype == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                body_text = payload.decode("utf-8", errors="replace")
                            break
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body_text = payload.decode("utf-8", errors="replace")

                results.append({
                    "from_email": from_email,
                    "subject": subject,
                    "body_text": body_text[:2000],  # truncate long bodies
                    "date": msg.get("Date", ""),
                    "message_id": message_id,
                })
            except Exception as e:
                logger.warning(f"Error parsing message {msg_id}: {e}")

        mail.logout()
    except Exception as exc:
        logger.error(f"[IMAP ERROR] {exc}")

    logger.info(f"Found {len(results)} unread replies via IMAP")
    return results
