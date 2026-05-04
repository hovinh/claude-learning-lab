import pytest
import requests as req_lib
from unittest.mock import MagicMock, patch

from api_monitor.config import EndpointConfig, ThresholdConfig
from api_monitor.monitor import APIMonitor, CheckResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def endpoint():
    return EndpointConfig(
        name="test-api",
        url="https://example.com/health",
        method="GET",
        expected_status=200,
        timeout=5,
        interval=30,
    )


@pytest.fixture()
def thresholds():
    return ThresholdConfig(response_time_ms=1000, error_rate=0.1, consecutive_failures=3)


@pytest.fixture()
def monitor(thresholds):
    return APIMonitor(thresholds)


def _mock_response(status: int = 200) -> MagicMock:
    r = MagicMock()
    r.status_code = status
    return r


# ---------------------------------------------------------------------------
# check_endpoint
# ---------------------------------------------------------------------------

class TestCheckEndpoint:
    def test_success(self, monitor, endpoint):
        with patch("requests.request", return_value=_mock_response(200)):
            result = monitor.check_endpoint(endpoint)
        assert result.success is True
        assert result.status_code == 200
        assert result.error is None

    def test_unexpected_status(self, monitor, endpoint):
        with patch("requests.request", return_value=_mock_response(500)):
            result = monitor.check_endpoint(endpoint)
        assert result.success is False
        assert "500" in result.error

    def test_timeout(self, monitor, endpoint):
        with patch("requests.request", side_effect=req_lib.exceptions.Timeout):
            result = monitor.check_endpoint(endpoint)
        assert result.success is False
        assert "timed out" in result.error

    def test_connection_error(self, monitor, endpoint):
        with patch("requests.request", side_effect=req_lib.exceptions.ConnectionError("refused")):
            result = monitor.check_endpoint(endpoint)
        assert result.success is False
        assert result.status_code is None

    def test_returns_check_result(self, monitor, endpoint):
        with patch("requests.request", return_value=_mock_response(200)):
            result = monitor.check_endpoint(endpoint)
        assert isinstance(result, CheckResult)
        assert result.endpoint_name == endpoint.name


# ---------------------------------------------------------------------------
# Stats accumulation
# ---------------------------------------------------------------------------

class TestEndpointStats:
    def test_uptime_80_percent(self, monitor, endpoint):
        with patch("requests.request", return_value=_mock_response(200)):
            for _ in range(8):
                monitor.check_endpoint(endpoint)
        with patch("requests.request", return_value=_mock_response(500)):
            for _ in range(2):
                monitor.check_endpoint(endpoint)
        stats = monitor.stats[endpoint.name]
        assert stats.uptime_percentage == pytest.approx(80.0)
        assert stats.error_rate == pytest.approx(0.2)

    def test_consecutive_failures_reset_on_success(self, monitor, endpoint):
        with patch("requests.request", return_value=_mock_response(500)):
            for _ in range(3):
                monitor.check_endpoint(endpoint)
        assert monitor.stats[endpoint.name].consecutive_failures == 3

        with patch("requests.request", return_value=_mock_response(200)):
            monitor.check_endpoint(endpoint)
        assert monitor.stats[endpoint.name].consecutive_failures == 0

    def test_response_times_recorded(self, monitor, endpoint):
        with patch("requests.request", return_value=_mock_response(200)):
            for _ in range(5):
                monitor.check_endpoint(endpoint)
        assert len(monitor.stats[endpoint.name].response_times) == 5

    def test_rolling_window_caps_at_1000(self, monitor, endpoint):
        with patch("requests.request", return_value=_mock_response(200)):
            for _ in range(1050):
                monitor.check_endpoint(endpoint)
        assert len(monitor.stats[endpoint.name].response_times) <= 1000


# ---------------------------------------------------------------------------
# Alert conditions
# ---------------------------------------------------------------------------

class TestAlertConditions:
    def test_alert_consecutive_failures(self, monitor, endpoint):
        with patch("requests.request", return_value=_mock_response(500)):
            for _ in range(3):
                monitor.check_endpoint(endpoint)
        should_alert, reasons = monitor.should_alert(endpoint.name)
        assert should_alert is True
        assert any("consecutive" in r.lower() for r in reasons)

    def test_no_alert_on_success(self, monitor, endpoint):
        with patch("requests.request", return_value=_mock_response(200)):
            monitor.check_endpoint(endpoint)
        should_alert, _ = monitor.should_alert(endpoint.name)
        assert should_alert is False

    def test_no_alert_for_unknown_endpoint(self, monitor):
        should_alert, reasons = monitor.should_alert("nonexistent")
        assert should_alert is False
        assert reasons == []

    def test_alert_on_high_error_rate(self, monitor, endpoint):
        # Thresholds: error_rate=0.1  →  2/10 = 0.2 should trigger
        with patch("requests.request", return_value=_mock_response(200)):
            for _ in range(8):
                monitor.check_endpoint(endpoint)
        with patch("requests.request", return_value=_mock_response(500)):
            for _ in range(2):
                monitor.check_endpoint(endpoint)
        # Reset consecutive_failures so only error_rate triggers
        monitor.stats[endpoint.name].consecutive_failures = 0
        should_alert, reasons = monitor.should_alert(endpoint.name)
        assert should_alert is True
        assert any("error rate" in r.lower() for r in reasons)
