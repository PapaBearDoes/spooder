"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================

MISSION:
    Give every chat a tiny spider friend that expresses emotions
    through ASCII art, one command at a time.

============================================================================
Configuration manager. Reads static config from .env and Docker Secrets.
----------------------------------------------------------------------------
FILE VERSION: v1.0.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

import os
from dataclasses import dataclass, field


# Default secrets path inside the container
SECRETS_DIR = "/run/secrets"


def _read_secret(path: str) -> str:
    """Read a Docker Secret from its file path. Strips trailing whitespace."""
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise RuntimeError(f"Docker Secret not found at: {path}")
    except PermissionError:
        raise RuntimeError(f"Cannot read Docker Secret at: {path} — permission denied")


@dataclass(frozen=True)
class ConfigManager:
    """Immutable static configuration for Spooder."""

    fluxer_token: str
    command_prefix: str = "!spooder"
    log_level: str = "INFO"


def create_config_manager() -> ConfigManager:
    """Factory function — reads .env vars and Docker Secrets at startup."""
    token = _read_secret(
        os.path.join(SECRETS_DIR, "spooder_fluxer_token")
    )

    prefix = os.getenv("SPOODER_COMMAND_PREFIX", "!spooder")
    log_level = os.getenv("SPOODER_LOG_LEVEL", "INFO")

    return ConfigManager(
        fluxer_token=token,
        command_prefix=prefix,
        log_level=log_level,
    )


__all__ = ["ConfigManager", "create_config_manager"]
