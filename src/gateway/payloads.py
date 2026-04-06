"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================
Gateway payload builders — IDENTIFY, RESUME, and HEARTBEAT opcodes.
----------------------------------------------------------------------------
FILE VERSION: v1.0.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

from src.gateway.constants import (
    OP_HEARTBEAT, OP_IDENTIFY, OP_RESUME,
    CLIENT_PROPERTIES, INTENTS_ALL,
)


def build_identify(token: str, intents: int = INTENTS_ALL) -> dict:
    """Build an IDENTIFY payload (opcode 2)."""
    return {
        "op": OP_IDENTIFY,
        "d": {
            "token": f"Bot {token}",
            "intents": intents,
            "properties": CLIENT_PROPERTIES,
            "compress": False,
            "large_threshold": 50,
        },
    }


def build_resume(token: str, session_id: str, sequence: int) -> dict:
    """Build a RESUME payload (opcode 6)."""
    return {
        "op": OP_RESUME,
        "d": {
            "token": f"Bot {token}",
            "session_id": session_id,
            "seq": sequence,
        },
    }


def build_heartbeat(sequence: int | None) -> dict:
    """Build a HEARTBEAT payload (opcode 1)."""
    return {
        "op": OP_HEARTBEAT,
        "d": sequence,
    }


__all__ = ["build_identify", "build_resume", "build_heartbeat"]
