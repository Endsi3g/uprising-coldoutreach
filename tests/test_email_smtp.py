"""Test email SMTP — mock smtplib, verify tracking injection."""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.services.email import prepare_html, render_template, send_smtp_email


def test_tracking_pixel_injection():
    html = "<html><body><p>Hello</p></body></html>"
    msg_id = uuid.uuid4()
    result = prepare_html(html, msg_id, add_pixel=True, track_clicks=False)
    assert f"/track/open/{msg_id}" in result
    assert 'width="1"' in result


def test_link_rewriting():
    html = '<a href="https://example.com/page">Click here</a>'
    msg_id = uuid.uuid4()
    result = prepare_html(html, msg_id, add_pixel=False, track_clicks=True)
    assert f"/track/click/{msg_id}" in result
    assert "url=https%3A%2F%2Fexample.com%2Fpage" in result
    assert "https://example.com/page" not in result.split("url=")[0]


def test_tracking_pixel_and_links_together():
    html = '<html><body><a href="https://site.com">Link</a></body></html>'
    msg_id = uuid.uuid4()
    result = prepare_html(html, msg_id, add_pixel=True, track_clicks=True)
    assert "/track/open/" in result
    assert "/track/click/" in result


def test_render_template():
    template = "Hello {{first_name}} from {{company_name}}!"
    result = render_template(template, {"first_name": "Jean", "company_name": "ACME"})
    assert result == "Hello Jean from ACME!"


def test_render_template_missing_var():
    template = "Hi {{first_name}}, your company {{company_name}} rocks."
    result = render_template(template, {"first_name": "Marie"})
    assert "Marie" in result
    assert "{{company_name}}" not in result  # replaced with empty


@patch("app.services.email.smtplib.SMTP_SSL")
def test_send_smtp_email_success(mock_smtp_class):
    mock_server = MagicMock()
    mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

    config = {
        "host": "smtp.gmail.com",
        "port": 465,
        "username": "test@gmail.com",
        "app_password": "test-pass",
        "from_name": "Test",
        "from_email": "test@gmail.com",
    }
    result = send_smtp_email(config, "dest@example.com", "Hello", "<p>Body</p>")
    assert result is True
    mock_server.login.assert_called_once()
    mock_server.sendmail.assert_called_once()


@patch("app.services.email.smtplib.SMTP_SSL")
def test_send_smtp_email_failure(mock_smtp_class):
    mock_smtp_class.side_effect = Exception("Connection refused")
    config = {
        "host": "smtp.gmail.com",
        "port": 465,
        "username": "test@gmail.com",
        "app_password": "test-pass",
    }
    result = send_smtp_email(config, "dest@example.com", "Hello", "<p>Body</p>")
    assert result is False
