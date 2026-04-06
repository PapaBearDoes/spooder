"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================

MISSION:
    Give every chat a tiny spider friend that expresses emotions
    through ASCII art, one command at a time.

============================================================================
Logging configuration manager. Provides colorized, human-readable log output
with a custom SUCCESS level (25).
----------------------------------------------------------------------------
FILE VERSION: v1.0.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

import logging
import sys

# ---------------------------------------------------------------------------
# Custom SUCCESS level (between INFO=20 and WARNING=30)
# ---------------------------------------------------------------------------
SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


def _success(self, message, *args, **kwargs):
    """Custom SUCCESS log method."""
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)


# Monkey-patch the success method onto Logger
logging.Logger.success = _success


# ---------------------------------------------------------------------------
# ANSI color codes
# ---------------------------------------------------------------------------
COLORS = {
    "CRITICAL": "\033[1;91m",  # Bright Red (Bold)
    "ERROR":    "\033[91m",    # Red
    "WARNING":  "\033[93m",    # Yellow
    "SUCCESS":  "\033[92m",    # Green
    "INFO":     "\033[96m",    # Cyan
    "DEBUG":    "\033[90m",    # Gray
}

SYMBOLS = {
    "CRITICAL": "🚨",
    "ERROR":    "❌",
    "WARNING":  "⚠️",
    "SUCCESS":  "✅",
    "INFO":     "ℹ️",
    "DEBUG":    "🔍",
}

RESET = "\033[0m"

# Libraries to silence
NOISY_LOGGERS = ("httpx", "httpcore", "websockets", "hpack", "asyncio")


class ColorFormatter(logging.Formatter):
    """Human-readable formatter with ANSI colors and emoji symbols."""

    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        color = COLORS.get(level, "")
        symbol = SYMBOLS.get(level, "")
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")

        msg = record.getMessage()
        formatted = (
            f"[{timestamp}] {color}{level:<8}{RESET} "
            f"| {record.name:<30} | {symbol} {msg}"
        )

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            formatted += f"\n{record.exc_text}"

        return formatted


class LoggingConfigManager:
    """Manages logging configuration for the Spooder process."""

    def __init__(self, level: str = "INFO") -> None:
        self._level = getattr(logging, level.upper(), logging.INFO)

    def setup(self) -> None:
        """Configure root logger with colorized output."""
        root = logging.getLogger()
        root.setLevel(self._level)

        # Clear existing handlers
        root.handlers.clear()

        # Console handler with color formatter
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(self._level)
        handler.setFormatter(ColorFormatter())
        root.addHandler(handler)

        # Silence noisy libraries
        for name in NOISY_LOGGERS:
            logging.getLogger(name).setLevel(logging.WARNING)

    def get_logger(self, name: str) -> logging.Logger:
        """Return a named logger."""
        return logging.getLogger(name)


def create_logging_config_manager(level: str = "INFO") -> LoggingConfigManager:
    """Factory function for LoggingConfigManager."""
    mgr = LoggingConfigManager(level=level)
    mgr.setup()
    return mgr


__all__ = ["LoggingConfigManager", "create_logging_config_manager"]
