"""SMS sending via TextBelt — free, open-source Twilio alternative.

Supports two modes:
  1. Self-hosted TextBelt server (TEXTBELT_URL points to your own instance)
  2. Public textbelt.com API (free tier: 1 SMS/day, paid: $0.005/SMS)

Docs: https://textbelt.com/  |  https://github.com/typpo/textbelt
"""

from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("sms")

DEFAULT_TEXTBELT_URL = "https://textbelt.com/text"


def send_sms(
    to_phone: str,
    message: str,
    api_key: str | None = None,
    textbelt_url: str | None = None,
) -> dict:
    """Send an SMS using TextBelt.

    Returns dict with keys: success (bool), textId (str), quotaRemaining (int).
    """
    url = textbelt_url or settings.TEXTBELT_URL or DEFAULT_TEXTBELT_URL
    key = api_key or settings.TEXTBELT_API_KEY or "textbelt"  # "textbelt" = free tier key

    payload = {
        "phone": to_phone,
        "message": message,
        "key": key,
    }

    try:
        resp = httpx.post(url, data=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("success"):
            logger.info(f"SMS sent to {to_phone} (textId={data.get('textId')})")
        else:
            logger.warning(f"SMS failed for {to_phone}: {data.get('error', 'unknown')}")
        return data
    except Exception as exc:
        logger.error(f"[SMS ERROR] {exc}")
        return {"success": False, "error": str(exc)}


def check_sms_status(text_id: str, textbelt_url: str | None = None) -> dict:
    """Check delivery status of a previously sent SMS."""
    base = textbelt_url or settings.TEXTBELT_URL or DEFAULT_TEXTBELT_URL
    # Status endpoint is /status/<textId>
    url = base.replace("/text", f"/status/{text_id}")

    try:
        resp = httpx.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.error(f"[SMS STATUS ERROR] {exc}")
        return {"status": "UNKNOWN", "error": str(exc)}
