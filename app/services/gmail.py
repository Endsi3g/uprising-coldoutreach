"""Gmail API integration — OAuth2 flow + send via Gmail REST API.

Higher deliverability than raw SMTP, no app-password needed.
Uses google-auth-oauthlib + google-api-python-client.
"""

from __future__ import annotations

import base64
import json
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from app.core.config import settings

logger = logging.getLogger("gmail")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
]


def get_auth_url(redirect_uri: str | None = None) -> str:
    """Generate the Google OAuth2 consent URL."""
    uri = redirect_uri or settings.GMAIL_REDIRECT_URI
    params = {
        "client_id": settings.GMAIL_CLIENT_ID,
        "redirect_uri": uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{qs}"


def exchange_code(code: str, redirect_uri: str | None = None) -> dict:
    """Exchange authorization code for access + refresh tokens.

    Returns dict: {access_token, refresh_token, expires_in, token_type, scope}
    """
    uri = redirect_uri or settings.GMAIL_REDIRECT_URI
    payload = {
        "code": code,
        "client_id": settings.GMAIL_CLIENT_ID,
        "client_secret": settings.GMAIL_CLIENT_SECRET,
        "redirect_uri": uri,
        "grant_type": "authorization_code",
    }
    resp = httpx.post(GOOGLE_TOKEN_URL, data=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    logger.info("Gmail OAuth tokens obtained successfully")
    return data


def refresh_access_token(refresh_token: str) -> dict:
    """Refresh an expired access token."""
    payload = {
        "client_id": settings.GMAIL_CLIENT_ID,
        "client_secret": settings.GMAIL_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    resp = httpx.post(GOOGLE_TOKEN_URL, data=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_user_email(access_token: str) -> str:
    """Get the authenticated user's email address."""
    resp = httpx.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("email", "")


def send_gmail_api(
    access_token: str,
    to_email: str,
    subject: str,
    body_html: str,
    from_email: str = "",
    from_name: str = "",
) -> dict:
    """Send an email via Gmail API.

    Returns dict with id and threadId on success.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    if from_name and from_email:
        msg["From"] = f"{from_name} <{from_email}>"
    elif from_email:
        msg["From"] = from_email
    msg["To"] = to_email

    # Plain text fallback
    import html as html_mod
    import re
    plain = html_mod.unescape(re.sub(r"<[^>]+>", "", body_html))
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    try:
        resp = httpx.post(
            GMAIL_SEND_URL,
            json={"raw": raw},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Gmail API sent to {to_email} (id={data.get('id')})")
        return data
    except Exception as exc:
        logger.error(f"[GMAIL API ERROR] {exc}")
        return {"error": str(exc)}
