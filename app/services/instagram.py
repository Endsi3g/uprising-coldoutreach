"""Instagram DM automation via Instagram Graph API (Facebook Business).

Prerequisites:
  1. Facebook App with Instagram Messaging permission
  2. Instagram Business/Creator account linked to Facebook Page
  3. Page access token with `instagram_manage_messages` scope

Docs: https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login
"""

from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger("instagram")

FB_GRAPH_BASE = "https://graph.facebook.com/v21.0"
FB_AUTH_URL = "https://www.facebook.com/v21.0/dialog/oauth"
FB_TOKEN_URL = f"{FB_GRAPH_BASE}/oauth/access_token"


def get_auth_url(redirect_uri: str | None = None) -> str:
    """Generate the Facebook/Instagram OAuth consent URL."""
    uri = redirect_uri or settings.INSTAGRAM_REDIRECT_URI
    params = {
        "client_id": settings.INSTAGRAM_APP_ID,
        "redirect_uri": uri,
        "scope": "instagram_manage_messages,pages_messaging,pages_manage_metadata",
        "response_type": "code",
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{FB_AUTH_URL}?{qs}"


def exchange_code(code: str, redirect_uri: str | None = None) -> dict:
    """Exchange authorization code for short-lived token, then get long-lived.

    Returns dict: {access_token, token_type, expires_in}
    """
    uri = redirect_uri or settings.INSTAGRAM_REDIRECT_URI

    # Step 1: short-lived token
    resp = httpx.get(
        FB_TOKEN_URL,
        params={
            "client_id": settings.INSTAGRAM_APP_ID,
            "client_secret": settings.INSTAGRAM_APP_SECRET,
            "redirect_uri": uri,
            "code": code,
        },
        timeout=30,
    )
    resp.raise_for_status()
    short_token = resp.json().get("access_token", "")

    # Step 2: exchange for long-lived token (60 days)
    resp2 = httpx.get(
        f"{FB_GRAPH_BASE}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": settings.INSTAGRAM_APP_ID,
            "client_secret": settings.INSTAGRAM_APP_SECRET,
            "fb_exchange_token": short_token,
        },
        timeout=30,
    )
    resp2.raise_for_status()
    data = resp2.json()
    logger.info("Instagram long-lived token obtained")
    return data


def get_instagram_business_account(page_access_token: str) -> dict:
    """Get the Instagram Business account linked to the Facebook Page."""
    # First, get the list of pages
    resp = httpx.get(
        f"{FB_GRAPH_BASE}/me/accounts",
        params={"access_token": page_access_token},
        timeout=15,
    )
    resp.raise_for_status()
    pages = resp.json().get("data", [])
    if not pages:
        return {"error": "No Facebook pages found"}

    page = pages[0]
    page_id = page["id"]
    page_token = page["access_token"]

    # Get IG account linked to page
    resp2 = httpx.get(
        f"{FB_GRAPH_BASE}/{page_id}",
        params={"fields": "instagram_business_account", "access_token": page_token},
        timeout=15,
    )
    resp2.raise_for_status()
    ig_data = resp2.json().get("instagram_business_account", {})

    return {
        "ig_account_id": ig_data.get("id"),
        "page_id": page_id,
        "page_access_token": page_token,
    }


def send_dm(
    page_access_token: str,
    recipient_ig_scoped_id: str,
    message: str,
) -> dict:
    """Send an Instagram DM via the Graph API.

    The recipient must have messaged the IG business account first
    (Instagram policy: 24-hour messaging window).
    """
    url = f"{FB_GRAPH_BASE}/me/messages"
    payload = {
        "recipient": {"id": recipient_ig_scoped_id},
        "message": {"text": message},
    }
    headers = {"Authorization": f"Bearer {page_access_token}"}

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Instagram DM sent to {recipient_ig_scoped_id}")
        return data
    except Exception as exc:
        logger.error(f"[INSTAGRAM DM ERROR] {exc}")
        return {"error": str(exc)}
