import logging
import sys

from .config import LoggingConfig


def setup_logging(config: LoggingConfig) -> None:
    level = getattr(logging, config.level.upper(), logging.INFO)
    formatter = logging.Formatter(config.format)

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if config.file:
        handlers.append(logging.FileHandler(config.file, encoding="utf-8"))

    logger = logging.getLogger("api_monitor")
    logger.setLevel(level)
    # Avoid duplicate handlers if called more than once (e.g. in tests)
    if not logger.handlers:
        for h in handlers:
            h.setFormatter(formatter)
            logger.addHandler(h)
