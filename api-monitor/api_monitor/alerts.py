import logging
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import EmailConfig

logger = logging.getLogger(__name__)


class EmailAlert:
    def __init__(self, config: EmailConfig) -> None:
        self.config = config

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def send_down_alert(self, endpoint_name: str, url: str, reasons: list[str]) -> bool:
        subject = f"[API Monitor] ALERT: {endpoint_name} has issues"
        body = (
            f"API Monitor Alert\n"
            f"Timestamp : {_now()}\n"
            f"Endpoint  : {endpoint_name}\n"
            f"URL       : {url}\n\n"
            f"Issues detected:\n"
            + "\n".join(f"  • {r}" for r in reasons)
            + "\n\nPlease investigate immediately."
        )
        return self._send(subject, body)

    def send_recovery_alert(self, endpoint_name: str, url: str) -> bool:
        subject = f"[API Monitor] RECOVERED: {endpoint_name} is back up"
        body = (
            f"API Monitor Recovery\n"
            f"Timestamp : {_now()}\n"
            f"Endpoint  : {endpoint_name}\n"
            f"URL       : {url}\n\n"
            f"The endpoint has recovered and is responding normally."
        )
        return self._send(subject, body)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _send(self, subject: str, body: str) -> bool:
        if not self.config.enabled:
            logger.debug("Email alerts disabled — skipping send")
            return False

        if not self.config.to_addresses:
            logger.warning("No alert recipients configured")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.config.from_address
        msg["To"] = ", ".join(self.config.to_addresses)
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                if self.config.username:
                    server.login(self.config.username, self.config.password)
                server.sendmail(
                    self.config.from_address,
                    self.config.to_addresses,
                    msg.as_string(),
                )
            logger.info("Alert sent to %s", self.config.to_addresses)
            return True
        except smtplib.SMTPException as exc:
            logger.error("Failed to send alert email: %s", exc)
            return False


def _now() -> str:
    return datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
