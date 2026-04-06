"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================
Gateway heartbeat — keeps the WebSocket alive and detects zombie
connections (no ACK received before the next beat is due).
----------------------------------------------------------------------------
FILE VERSION: v1.0.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

import asyncio
import json
import random

from src.gateway.payloads import build_heartbeat


class Heartbeat:
    """Sends periodic heartbeats and detects zombie connections."""

    def __init__(self, ws, interval_ms: int, log) -> None:
        self._ws = ws
        self._interval: float = interval_ms / 1000.0
        self._log = log
        self._task: asyncio.Task | None = None
        self._ack_received: bool = True
        self._get_sequence = None

    def start(self, get_sequence_fn) -> None:
        """Start the heartbeat loop."""
        self._get_sequence = get_sequence_fn
        self._ack_received = True
        self._task = asyncio.create_task(self._loop())
        self._log.debug(f"Heartbeat started (interval: {self._interval:.1f}s)")

    def ack(self) -> None:
        """Mark that a HEARTBEAT_ACK was received."""
        self._ack_received = True

    def stop(self) -> None:
        """Cancel the heartbeat loop."""
        if self._task and not self._task.done():
            self._task.cancel()
            self._task = None
        self._log.debug("Heartbeat stopped")

    def update_ws(self, ws) -> None:
        """Update the WebSocket reference after reconnect."""
        self._ws = ws

    async def _loop(self) -> None:
        """Heartbeat loop with initial jitter."""
        try:
            jitter = self._interval * random.random()
            self._log.debug(f"First heartbeat in {jitter:.1f}s (jitter)")
            await asyncio.sleep(jitter)
            await self._send_beat()

            while True:
                await asyncio.sleep(self._interval)
                if not self._ack_received:
                    self._log.warning(
                        "Zombie connection detected — no HEARTBEAT_ACK. "
                        "Closing WebSocket."
                    )
                    await self._ws.close(4000)
                    return
                await self._send_beat()

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self._log.error(f"Heartbeat loop error: {e}")

    async def _send_beat(self) -> None:
        """Send a single heartbeat and reset the ACK flag."""
        seq = self._get_sequence() if self._get_sequence else None
        payload = build_heartbeat(seq)
        try:
            self._ack_received = False
            await self._ws.send(json.dumps(payload))
            self._log.debug(f"Heartbeat sent (seq={seq})")
        except Exception as e:
            self._log.warning(f"Failed to send heartbeat: {e}")


__all__ = ["Heartbeat"]
