"""Email sending via SMTP (Gmail) with tracking pixel and click rewriting."""

from __future__ import annotations

import re
import smtplib
import ssl
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import quote

from app.core.config import settings


def _build_tracking_pixel(message_id: uuid.UUID) -> str:
    base = settings.TRACKING_BASE_URL.rstrip("/")
    return f'<img src="{base}/track/open/{message_id}" width="1" height="1" style="display:none" />'


def _rewrite_links(html: str, message_id: uuid.UUID) -> str:
    """Replace <a href="..."> links with tracked redirect URLs."""
    base = settings.TRACKING_BASE_URL.rstrip("/")

    def _replace(match: re.Match) -> str:
        original_url = match.group(1)
        tracked = f'{base}/track/click/{message_id}?url={quote(original_url, safe="")}'
        return f'href="{tracked}"'

    return re.sub(r'href="(https?://[^"]+)"', _replace, html, flags=re.IGNORECASE)


def prepare_html(
    body_html: str,
    message_id: uuid.UUID,
    add_pixel: bool = True,
    track_clicks: bool = True,
) -> str:
    """Inject tracking pixel and rewrite links in email HTML."""
    html = body_html
    if track_clicks:
        html = _rewrite_links(html, message_id)
    if add_pixel:
        # append before </body> if present, otherwise at end
        pixel = _build_tracking_pixel(message_id)
        if "</body>" in html.lower():
            html = re.sub(r"(</body>)", f"{pixel}\\1", html, flags=re.IGNORECASE)
        else:
            html += pixel
    return html


def send_smtp_email(
    smtp_config: dict,
    to_email: str,
    subject: str,
    body_html: str,
) -> bool:
    """Send an email using SMTP config from outbound_identity.

    Expected smtp_config keys:
      host, port, username, app_password, from_name, from_email
    """
    host = smtp_config.get("host", "smtp.gmail.com")
    port = int(smtp_config.get("port", 465))
    username = smtp_config["username"]
    app_password = smtp_config["app_password"]
    from_name = smtp_config.get("from_name", "")
    from_email = smtp_config.get("from_email", username)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>" if from_name else from_email
    msg["To"] = to_email

    # plain text fallback
    import html as html_mod
    plain = html_mod.unescape(re.sub(r"<[^>]+>", "", body_html))
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    context = ssl.create_default_context()
    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, context=context) as server:
                server.login(username, app_password)
                server.sendmail(from_email, to_email, msg.as_string())
        else:
            with smtplib.SMTP(host, port) as server:
                server.starttls(context=context)
                server.login(username, app_password)
                server.sendmail(from_email, to_email, msg.as_string())
        return True
    except Exception as exc:
        # Log the error in production
        print(f"[EMAIL ERROR] {exc}")
        return False


def render_template(template: str, lead_data: dict) -> str:
    """Replace {{variable}} placeholders with lead data."""
    import re
    result = template
    for key, value in lead_data.items():
        result = result.replace("{{" + key + "}}", str(value or ""))
    # Strip any remaining unreplaced placeholders
    result = re.sub(r"\{\{[^}]*\}\}", "", result)
    return result
