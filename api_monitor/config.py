import os
from dataclasses import dataclass, field
from typing import Optional
import yaml


@dataclass
class EndpointConfig:
    name: str
    url: str
    method: str = "GET"
    expected_status: int = 200
    timeout: int = 10
    interval: int = 60
    headers: dict = field(default_factory=dict)
    body: Optional[dict] = None


@dataclass
class ThresholdConfig:
    response_time_ms: int = 2000
    error_rate: float = 0.1
    consecutive_failures: int = 3


@dataclass
class EmailConfig:
    enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    use_tls: bool = True
    username: str = ""
    password: str = ""
    from_address: str = ""
    to_addresses: list = field(default_factory=list)


@dataclass
class AlertsConfig:
    email: EmailConfig = field(default_factory=EmailConfig)


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: Optional[str] = None
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class AppConfig:
    endpoints: list = field(default_factory=list)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    alerts: AlertsConfig = field(default_factory=AlertsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


def load_config(config_path: str) -> AppConfig:
    with open(config_path) as f:
        data = yaml.safe_load(f) or {}

    endpoints = [EndpointConfig(**ep) for ep in data.get("endpoints", [])]

    thresholds = ThresholdConfig(**data.get("thresholds", {}))

    email_data = data.get("alerts", {}).get("email", {})
    # Credentials can be injected via env vars to avoid storing secrets in YAML
    email_data["username"] = os.getenv("MONITOR_SMTP_USERNAME", email_data.get("username", ""))
    email_data["password"] = os.getenv("MONITOR_SMTP_PASSWORD", email_data.get("password", ""))
    alerts = AlertsConfig(email=EmailConfig(**email_data))

    logging_cfg = LoggingConfig(**data.get("logging", {}))

    return AppConfig(
        endpoints=endpoints,
        thresholds=thresholds,
        alerts=alerts,
        logging=logging_cfg,
    )
