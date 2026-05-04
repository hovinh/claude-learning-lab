import smtplib
import pytest
from unittest.mock import MagicMock, patch

from api_monitor.alerts import EmailAlert
from api_monitor.config import EmailConfig


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def email_config():
    return EmailConfig(
        enabled=True,
        smtp_host="smtp.example.com",
        smtp_port=587,
        use_tls=True,
        username="user@example.com",
        password="secret",
        from_address="monitor@example.com",
        to_addresses=["admin@example.com"],
    )


@pytest.fixture()
def alerter(email_config):
    return EmailAlert(email_config)


def _patched_smtp():
    """Return a context-manager-compatible SMTP mock."""
    mock_server = MagicMock()
    smtp_cls = MagicMock()
    smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
    smtp_cls.return_value.__exit__ = MagicMock(return_value=False)
    return smtp_cls, mock_server


# ---------------------------------------------------------------------------
# _send (via send_down_alert / send_recovery_alert)
# ---------------------------------------------------------------------------

class TestEmailAlert:
    def test_sends_when_enabled(self, alerter):
        smtp_cls, server = _patched_smtp()
        with patch("smtplib.SMTP", smtp_cls):
            result = alerter.send_down_alert("my-api", "https://example.com", ["timeout"])
        assert result is True
        server.sendmail.assert_called_once()

    def test_skips_when_disabled(self, email_config):
        email_config.enabled = False
        smtp_cls, _ = _patched_smtp()
        with patch("smtplib.SMTP", smtp_cls):
            result = EmailAlert(email_config).send_down_alert("api", "http://x", ["err"])
        smtp_cls.assert_not_called()
        assert result is False

    def test_skips_when_no_recipients(self, email_config):
        email_config.to_addresses = []
        result = EmailAlert(email_config).send_down_alert("api", "http://x", ["err"])
        assert result is False

    def test_returns_false_on_smtp_error(self, alerter):
        with patch("smtplib.SMTP", side_effect=smtplib.SMTPException("conn failed")):
            result = alerter.send_down_alert("api", "http://x", ["err"])
        assert result is False

    def test_down_alert_body_contains_reasons(self, alerter):
        import email as email_lib

        captured: dict = {}
        smtp_cls, server = _patched_smtp()
        server.sendmail.side_effect = lambda f, t, msg: captured.update({"msg": msg})
        with patch("smtplib.SMTP", smtp_cls):
            alerter.send_down_alert("my-api", "https://example.com", ["timeout", "high error rate"])

        # Parse and decode the MIME message so we can search plain text
        msg = email_lib.message_from_string(captured.get("msg", ""))
        body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
        assert "timeout" in body
        assert "high error rate" in body

    def test_recovery_alert_sent(self, alerter):
        smtp_cls, server = _patched_smtp()
        with patch("smtplib.SMTP", smtp_cls):
            result = alerter.send_recovery_alert("my-api", "https://example.com")
        assert result is True
        server.sendmail.assert_called_once()

    def test_starttls_called_when_use_tls(self, alerter):
        smtp_cls, server = _patched_smtp()
        with patch("smtplib.SMTP", smtp_cls):
            alerter.send_down_alert("api", "http://x", ["err"])
        server.starttls.assert_called_once()

    def test_login_called_with_credentials(self, alerter):
        smtp_cls, server = _patched_smtp()
        with patch("smtplib.SMTP", smtp_cls):
            alerter.send_down_alert("api", "http://x", ["err"])
        server.login.assert_called_once_with("user@example.com", "secret")
