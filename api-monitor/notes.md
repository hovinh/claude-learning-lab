# api-monitor — Notes

## Original prompt

> Create a Python CLI tool using Click and Requests to monitor a REST API endpoint
> for uptime, response time, and error rates. Include Logging, config file YAML,
> and alerts via email (use smtplib). Structure as a package with tests (pytest).

## Concepts demonstrated

### Python package structure
- `pyproject.toml` with `[project.scripts]` to expose a CLI entry point
- Editable install (`pip install -e .`) lets source changes take effect immediately
- `*.egg-info/` is generated metadata — never commit it

### Click (CLI framework)
- `@click.group()` creates a root command that holds sub-commands (`check`, `start`, `status`)
- `@click.option()` declares flags; `type=int` validates input before your code runs
- `@click.pass_context` + `ctx.obj` threads shared state (loaded config) down to sub-commands without globals
- `click.echo` / `click.style` handle encoding edge cases and ANSI colour gracefully

### Configuration — YAML + dataclasses
- `yaml.safe_load` reads the file; plain dataclasses (`@dataclass`) give typed, IDE-friendly config objects
- Secrets (SMTP credentials) are never stored in YAML — injected via env vars (`MONITOR_SMTP_USERNAME`, `MONITOR_SMTP_PASSWORD`) so the config file is safe to commit

### Logging
- Use `logging.getLogger(__name__)` in every module — gives clean hierarchical names (`api_monitor.monitor`)
- One `setup_logging()` call at startup configures the root `api_monitor` logger; all child loggers inherit it
- Guard against duplicate handlers: check `if not logger.handlers` before adding, otherwise pytest re-runs add handlers repeatedly
- Prefer `logger.debug("val: %s", x)` over `logger.debug(f"val: {x}")` — `%s` is lazily evaluated and skips string construction when the level is disabled

### Email alerts (smtplib)
- `MIMEMultipart` + `MIMEText` builds a proper MIME message; `starttls()` upgrades the connection before `login()`
- Alert spam is suppressed by tracking a `alerted: set[str]` — fires once on transition *down*, then once on *recovery*
- `send_down_alert` and `send_recovery_alert` are separate methods so callers are explicit about intent

### Testing (pytest)
- `unittest.mock.patch` replaces `requests.request` and `smtplib.SMTP` — tests never make real network calls
- `pytest.fixture` shares setup (endpoint config, monitor instance) across tests without repetition
- `monkeypatch.setenv` tests env-var overrides without polluting the real environment
- MIME message bodies are base64-encoded — decode with `part.get_payload(decode=True)` before asserting on content
- `tmp_path` (built-in pytest fixture) gives a fresh temp directory per test; no manual cleanup needed

### Stats design
- Rolling window of 1 000 samples per endpoint keeps memory bounded in long-running processes
- `statistics.mean` / sorted-index p95 are computed on-the-fly — no external library needed for this scale
- `consecutive_failures` resets to 0 on the first success, enabling clean recovery detection

## Claude Code workflow

- The entire package was generated in one prompt, then iterated via conversation
- Build backend typo (`setuptools.backends.legacy:build` → `setuptools.build_meta`) caught by running `pip install -e .` immediately after generation — always install and test before declaring done
- One test failed post-generation (`test_down_alert_body_contains_reasons`) because MIME encodes text as base64; fixed by parsing the message with the stdlib `email` module instead of checking the raw string
- Comments were intentionally omitted from source — well-named identifiers explain the *what*; comments are reserved for non-obvious *why* (hidden constraints, protocol ordering, invariants)
