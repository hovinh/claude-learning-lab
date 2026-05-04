import logging
import sys
import time
from typing import Optional

import click

from .alerts import EmailAlert
from .config import load_config
from .logger import setup_logging
from .monitor import APIMonitor

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------

@click.group()
@click.option(
    "--config", "-c",
    default="config.yaml",
    show_default=True,
    help="Path to YAML configuration file.",
)
@click.pass_context
def cli(ctx: click.Context, config: str) -> None:
    """Monitor REST API endpoints for uptime, latency, and error rates."""
    ctx.ensure_object(dict)
    try:
        app_config = load_config(config)
    except FileNotFoundError:
        click.echo(f"Config file not found: {config}", err=True)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Failed to load config: {exc}", err=True)
        sys.exit(1)

    setup_logging(app_config.logging)
    ctx.obj["config"] = app_config


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@cli.command()
@click.pass_context
def check(ctx: click.Context) -> None:
    """Run a single check of all configured endpoints and exit."""
    app_config = ctx.obj["config"]
    monitor = APIMonitor(app_config.thresholds)
    alerter = EmailAlert(app_config.alerts.email)
    exit_code = 0

    for endpoint in app_config.endpoints:
        result = monitor.check_endpoint(endpoint)
        tag = click.style("OK  ", fg="green") if result.success else click.style("FAIL", fg="red")
        code = result.status_code or "N/A"
        line = f"[{tag}] {endpoint.name:<30} HTTP {code:<5} {result.response_time_ms:.0f}ms"
        if result.error:
            line += f"  — {result.error}"
        click.echo(line)

        should_alert, reasons = monitor.should_alert(endpoint.name)
        if should_alert:
            alerter.send_down_alert(endpoint.name, endpoint.url, reasons)
            exit_code = 1

    sys.exit(exit_code)


@cli.command()
@click.option(
    "--interval", "-i",
    default=None,
    type=int,
    help="Override per-endpoint check interval (seconds).",
)
@click.option(
    "--duration", "-d",
    default=None,
    type=int,
    help="Stop after N seconds (default: run until Ctrl-C).",
)
@click.pass_context
def start(ctx: click.Context, interval: Optional[int], duration: Optional[int]) -> None:
    """Start continuous monitoring of all configured endpoints."""
    app_config = ctx.obj["config"]
    monitor = APIMonitor(app_config.thresholds)
    alerter = EmailAlert(app_config.alerts.email)

    # Track alert state per-endpoint to send recovery notices and suppress spam
    alerted: set[str] = set()

    sleep_secs = interval or min(ep.interval for ep in app_config.endpoints)
    click.echo(f"Monitoring {len(app_config.endpoints)} endpoint(s) every {sleep_secs}s. Ctrl-C to stop.")

    start_ts = time.monotonic()
    try:
        while True:
            for endpoint in app_config.endpoints:
                monitor.check_endpoint(endpoint)

                should_alert, reasons = monitor.should_alert(endpoint.name)
                if should_alert and endpoint.name not in alerted:
                    alerted.add(endpoint.name)
                    alerter.send_down_alert(endpoint.name, endpoint.url, reasons)
                elif not should_alert and endpoint.name in alerted:
                    alerted.discard(endpoint.name)
                    alerter.send_recovery_alert(endpoint.name, endpoint.url)

            if duration and (time.monotonic() - start_ts) >= duration:
                break
            time.sleep(sleep_secs)

    except KeyboardInterrupt:
        pass
    finally:
        click.echo(monitor.get_summary())


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Run one check and print a formatted status table."""
    app_config = ctx.obj["config"]
    monitor = APIMonitor(app_config.thresholds)

    results = [monitor.check_endpoint(ep) for ep in app_config.endpoints]

    click.echo(f"\n{'Endpoint':<30} {'Status':<6} {'HTTP':<6} {'ms':>8}")
    click.echo("─" * 56)
    for r in results:
        tag = click.style("UP  ", fg="green") if r.success else click.style("DOWN", fg="red")
        click.echo(
            f"{r.endpoint_name:<30} {tag}   {str(r.status_code or 'N/A'):<6} {r.response_time_ms:>8.0f}"
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    cli(obj={})


if __name__ == "__main__":
    main()
