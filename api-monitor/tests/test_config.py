import pytest
import yaml

from api_monitor.config import AppConfig, load_config

SAMPLE = {
    "endpoints": [
        {
            "name": "test-api",
            "url": "https://example.com/health",
            "method": "GET",
            "expected_status": 200,
            "timeout": 5,
            "interval": 30,
        }
    ],
    "thresholds": {
        "response_time_ms": 1000,
        "error_rate": 0.05,
        "consecutive_failures": 2,
    },
    "alerts": {
        "email": {
            "enabled": False,
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "use_tls": True,
            "username": "",
            "password": "",
            "from_address": "monitor@example.com",
            "to_addresses": ["admin@example.com"],
        }
    },
    "logging": {"level": "DEBUG", "format": "%(message)s"},
}


@pytest.fixture()
def config_file(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(SAMPLE), encoding="utf-8")
    return str(path)


def test_returns_app_config(config_file):
    assert isinstance(load_config(config_file), AppConfig)


def test_endpoints_parsed(config_file):
    config = load_config(config_file)
    assert len(config.endpoints) == 1
    ep = config.endpoints[0]
    assert ep.name == "test-api"
    assert ep.url == "https://example.com/health"
    assert ep.timeout == 5
    assert ep.interval == 30


def test_thresholds_parsed(config_file):
    t = load_config(config_file).thresholds
    assert t.response_time_ms == 1000
    assert t.error_rate == pytest.approx(0.05)
    assert t.consecutive_failures == 2


def test_email_config_parsed(config_file):
    email = load_config(config_file).alerts.email
    assert email.enabled is False
    assert email.smtp_host == "smtp.example.com"
    assert email.to_addresses == ["admin@example.com"]


def test_env_var_overrides_credentials(config_file, monkeypatch):
    monkeypatch.setenv("MONITOR_SMTP_USERNAME", "env_user")
    monkeypatch.setenv("MONITOR_SMTP_PASSWORD", "env_pass")
    email = load_config(config_file).alerts.email
    assert email.username == "env_user"
    assert email.password == "env_pass"


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.yaml")
