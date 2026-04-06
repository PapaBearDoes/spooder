"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================
Gateway constants — opcodes, close codes, intents, and API URLs.
Sourced from Fluxer gateway docs and Skald's empirical findings.
----------------------------------------------------------------------------
FILE VERSION: v1.0.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

# ── Fluxer API ────────────────────────────────────────────────────────────

API_BASE = "https://api.fluxer.app/v1"
GATEWAY_DISCOVER = f"{API_BASE}/gateway/bot"
GATEWAY_VERSION = 1  # Fluxer uses v=1

# ── Gateway Opcodes ───────────────────────────────────────────────────────

OP_DISPATCH = 0
OP_HEARTBEAT = 1
OP_IDENTIFY = 2
OP_RESUME = 6
OP_RECONNECT = 7
OP_INVALID_SESSION = 9
OP_HELLO = 10
OP_HEARTBEAT_ACK = 11
OP_GATEWAY_ERROR = 12

# ── Gateway Close Codes ──────────────────────────────────────────────────

CLOSE_AUTHENTICATION_FAILED = 4004
CLOSE_NOT_AUTHENTICATED = 4003
CLOSE_INVALID_SEQ = 4007
CLOSE_SESSION_TIMEOUT = 4009
CLOSE_INVALID_SHARD = 4010
CLOSE_SHARDING_REQUIRED = 4011
CLOSE_INVALID_API_VERSION = 4012

FATAL_CLOSE_CODES = frozenset(
    {
        CLOSE_AUTHENTICATION_FAILED,
        CLOSE_INVALID_SHARD,
        CLOSE_SHARDING_REQUIRED,
        CLOSE_INVALID_API_VERSION,
    }
)

RE_IDENTIFY_CLOSE_CODES = frozenset(
    {
        CLOSE_NOT_AUTHENTICATED,
        CLOSE_INVALID_SEQ,
        CLOSE_SESSION_TIMEOUT,
    }
)

# ── Intents ──────────────────────────────────────────────────────────────

INTENTS_ALL = 0xFFFF  # 65535 — all bits set

# ── Gateway Payload Keys ─────────────────────────────────────────────────

KEY_OP = "op"
KEY_DATA = "d"
KEY_SEQUENCE = "s"
KEY_EVENT = "t"

# ── Client Properties ────────────────────────────────────────────────────

CLIENT_PROPERTIES = {
    "os": "linux",
    "browser": "spooder",
    "device": "spooder",
}


__all__ = [
    "API_BASE", "GATEWAY_DISCOVER", "GATEWAY_VERSION",
    "OP_DISPATCH", "OP_HEARTBEAT", "OP_IDENTIFY", "OP_RESUME",
    "OP_RECONNECT", "OP_INVALID_SESSION", "OP_HELLO",
    "OP_HEARTBEAT_ACK", "OP_GATEWAY_ERROR",
    "FATAL_CLOSE_CODES", "RE_IDENTIFY_CLOSE_CODES",
    "INTENTS_ALL", "KEY_OP", "KEY_DATA", "KEY_SEQUENCE", "KEY_EVENT",
    "CLIENT_PROPERTIES",
]
