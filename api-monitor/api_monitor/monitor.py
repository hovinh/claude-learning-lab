import statistics
import time
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import requests

from .config import EndpointConfig, ThresholdConfig

logger = logging.getLogger(__name__)

# Rolling window size for response-time statistics
_ROLLING_WINDOW = 1000


@dataclass
class CheckResult:
    endpoint_name: str
    url: str
    timestamp: datetime
    status_code: Optional[int]
    response_time_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class EndpointStats:
    name: str
    url: str
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    response_times: list = field(default_factory=list)
    consecutive_failures: int = 0
    last_check: Optional[CheckResult] = None

    @property
    def uptime_percentage(self) -> float:
        if self.total_checks == 0:
            return 0.0
        return (self.successful_checks / self.total_checks) * 100

    @property
    def error_rate(self) -> float:
        if self.total_checks == 0:
            return 0.0
        return self.failed_checks / self.total_checks

    @property
    def avg_response_time_ms(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0.0

    @property
    def p95_response_time_ms(self) -> float:
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        idx = min(int(0.95 * len(sorted_times)), len(sorted_times) - 1)
        return sorted_times[idx]


class APIMonitor:
    def __init__(self, thresholds: ThresholdConfig) -> None:
        self.thresholds = thresholds
        self.stats: dict[str, EndpointStats] = {}

    # ------------------------------------------------------------------
    # Core check
    # ------------------------------------------------------------------

    def check_endpoint(self, endpoint: EndpointConfig) -> CheckResult:
        start = time.monotonic()
        timestamp = datetime.now(tz=timezone.utc)

        try:
            response = requests.request(
                method=endpoint.method,
                url=endpoint.url,
                headers=endpoint.headers,
                json=endpoint.body,
                timeout=endpoint.timeout,
            )
            elapsed_ms = (time.monotonic() - start) * 1000
            success = response.status_code == endpoint.expected_status
            result = CheckResult(
                endpoint_name=endpoint.name,
                url=endpoint.url,
                timestamp=timestamp,
                status_code=response.status_code,
                response_time_ms=elapsed_ms,
                success=success,
                error=None
                if success
                else f"Expected HTTP {endpoint.expected_status}, got {response.status_code}",
            )
        except requests.exceptions.Timeout:
            elapsed_ms = (time.monotonic() - start) * 1000
            result = CheckResult(
                endpoint_name=endpoint.name,
                url=endpoint.url,
                timestamp=timestamp,
                status_code=None,
                response_time_ms=elapsed_ms,
                success=False,
                error="Request timed out",
            )
        except requests.exceptions.RequestException as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            result = CheckResult(
                endpoint_name=endpoint.name,
                url=endpoint.url,
                timestamp=timestamp,
                status_code=None,
                response_time_ms=elapsed_ms,
                success=False,
                error=str(exc),
            )

        self._update_stats(endpoint, result)
        self._log_result(result)
        return result

    # ------------------------------------------------------------------
    # Alert logic
    # ------------------------------------------------------------------

    def should_alert(self, endpoint_name: str) -> tuple[bool, list[str]]:
        stats = self.stats.get(endpoint_name)
        if not stats:
            return False, []

        reasons: list[str] = []

        if stats.consecutive_failures >= self.thresholds.consecutive_failures:
            reasons.append(
                f"Consecutive failures: {stats.consecutive_failures} "
                f"(threshold: {self.thresholds.consecutive_failures})"
            )

        if stats.avg_response_time_ms > self.thresholds.response_time_ms:
            reasons.append(
                f"Avg response time {stats.avg_response_time_ms:.0f}ms "
                f"exceeds {self.thresholds.response_time_ms}ms"
            )

        if stats.error_rate > self.thresholds.error_rate:
            reasons.append(
                f"Error rate {stats.error_rate:.1%} "
                f"exceeds {self.thresholds.error_rate:.1%}"
            )

        return bool(reasons), reasons

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_summary(self) -> str:
        if not self.stats:
            return "No checks performed yet."

        lines = ["", "API Monitor Summary", "=" * 56]
        for stats in self.stats.values():
            status = "UP" if (stats.last_check and stats.last_check.success) else "DOWN"
            lines += [
                f"\nEndpoint : {stats.name}",
                f"URL      : {stats.url}",
                f"Status   : {status}",
                f"Uptime   : {stats.uptime_percentage:.2f}% "
                f"({stats.successful_checks}/{stats.total_checks} checks)",
                f"Errors   : {stats.error_rate:.1%}",
                f"Resp avg : {stats.avg_response_time_ms:.0f}ms  "
                f"p95: {stats.p95_response_time_ms:.0f}ms",
            ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _update_stats(self, endpoint: EndpointConfig, result: CheckResult) -> None:
        name = endpoint.name
        if name not in self.stats:
            self.stats[name] = EndpointStats(name=name, url=endpoint.url)

        stats = self.stats[name]
        stats.total_checks += 1
        stats.last_check = result
        stats.response_times.append(result.response_time_ms)
        # Bounded rolling window to prevent unbounded memory growth
        if len(stats.response_times) > _ROLLING_WINDOW:
            stats.response_times = stats.response_times[-_ROLLING_WINDOW:]

        if result.success:
            stats.successful_checks += 1
            stats.consecutive_failures = 0
        else:
            stats.failed_checks += 1
            stats.consecutive_failures += 1

    def _log_result(self, result: CheckResult) -> None:
        code = result.status_code or "N/A"
        msg = (
            f"[{'OK' if result.success else 'FAIL'}] {result.endpoint_name} "
            f"HTTP {code} {result.response_time_ms:.0f}ms"
        )
        if result.error:
            msg += f" — {result.error}"
        if result.success:
            logger.info(msg)
        else:
            logger.warning(msg)
