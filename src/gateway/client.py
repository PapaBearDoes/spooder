"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================
SpooderGateway — native Fluxer gateway client.
Manages the full WebSocket lifecycle: connect → identify → heartbeat →
dispatch → resume/reconnect. Adapted from Fluxarr's FluxarrGateway.
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
import sys

import httpx
import websockets

from src.gateway.constants import (
    GATEWAY_DISCOVER, GATEWAY_VERSION,
    OP_DISPATCH, OP_HEARTBEAT, OP_HELLO, OP_HEARTBEAT_ACK,
    OP_RECONNECT, OP_INVALID_SESSION, OP_GATEWAY_ERROR,
    FATAL_CLOSE_CODES, RE_IDENTIFY_CLOSE_CODES,
    INTENTS_ALL, KEY_OP, KEY_DATA, KEY_SEQUENCE, KEY_EVENT,
)
from src.gateway.dispatcher import SpooderDispatcher
from src.gateway.heartbeat import Heartbeat
from src.gateway.payloads import build_identify, build_resume, build_heartbeat


class NonRecoverableError(Exception):
    """Raised when the gateway returns a fatal close code."""
    pass


class SpooderGateway:
    """Native Fluxer gateway client for Spooder."""

    def __init__(self, token: str, log, intents: int = INTENTS_ALL) -> None:
        self._token = token
        self._intents = intents
        self._log = log

        self.dispatcher = SpooderDispatcher(log)

        self._session_id: str | None = None
        self._sequence: int | None = None
        self._gateway_url: str | None = None

        self.bot_user: dict | None = None
        self.guilds: list[dict] = []

        self._ws = None
        self._heartbeat: Heartbeat | None = None
        self._shutdown = False

        self._backoff: float = 1.0
        self._max_backoff: float = 60.0

    # ── Public API ────────────────────────────────────────────────────────

    def on(self, event_name: str, handler) -> None:
        """Register a handler for a gateway event."""
        self.dispatcher.on(event_name, handler)

    async def run(self) -> None:
        """Connect to the gateway and run the event loop."""
        self._shutdown = False
        try:
            await self._discover_gateway()
            await self._connect(resume=False)
            await self._event_loop()
        except NonRecoverableError as e:
            self._log.critical(f"Fatal gateway error: {e}")
            sys.exit(1)
        except asyncio.CancelledError:
            self._log.info("Gateway cancelled")
        finally:
            await self._cleanup()

    async def close(self) -> None:
        """Graceful shutdown."""
        self._shutdown = True
        if self._heartbeat:
            self._heartbeat.stop()
        if self._ws:
            await self._ws.close(1000)
        self._log.info("Gateway connection closed")

    # ── Discovery ─────────────────────────────────────────────────────────

    async def _discover_gateway(self) -> None:
        """Fetch gateway URL from GET /gateway/bot."""
        self._log.info("Discovering gateway URL...")
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                GATEWAY_DISCOVER,
                headers={"Authorization": f"Bot {self._token}"},
            )
            if resp.status_code != 200:
                raise NonRecoverableError(
                    f"Gateway discovery failed: HTTP {resp.status_code} {resp.text}"
                )
            data = resp.json()

        self._gateway_url = data["url"]
        remaining = data.get("session_start_limit", {}).get("remaining", "?")
        total = data.get("session_start_limit", {}).get("total", "?")

        self._log.info(
            f"Gateway URL: {self._gateway_url} | Sessions: {remaining}/{total}"
        )
        if isinstance(remaining, int) and remaining < 10:
            self._log.warning(f"Low session start budget: {remaining} remaining")

    # ── Connect ───────────────────────────────────────────────────────────

    async def _connect(self, resume: bool = False) -> None:
        """Open WebSocket, receive HELLO, send IDENTIFY or RESUME."""
        if self._heartbeat:
            self._heartbeat.stop()

        ws_url = f"{self._gateway_url}/?v={GATEWAY_VERSION}&encoding=json"
        self._log.info(f"Connecting to {ws_url}...")
        self._ws = await websockets.connect(ws_url)

        # Receive HELLO (opcode 10)
        raw = await self._ws.recv()
        hello = json.loads(raw)
        if hello.get(KEY_OP) != OP_HELLO:
            raise NonRecoverableError(
                f"Expected opcode 10 (HELLO), got: {hello.get(KEY_OP)}"
            )

        heartbeat_interval = hello[KEY_DATA]["heartbeat_interval"]
        self._log.info(f"HELLO received (heartbeat_interval: {heartbeat_interval}ms)")

        # Start heartbeat
        self._heartbeat = Heartbeat(self._ws, heartbeat_interval, self._log)
        self._heartbeat.start(lambda: self._sequence)

        # Send IDENTIFY or RESUME
        if resume and self._session_id and self._sequence is not None:
            self._log.info(
                f"Resuming session {self._session_id} at seq {self._sequence}"
            )
            await self._ws.send(
                json.dumps(build_resume(self._token, self._session_id, self._sequence))
            )
        else:
            self._log.info("Sending IDENTIFY...")
            await self._ws.send(json.dumps(build_identify(self._token, self._intents)))

        # Reset backoff on successful connect
        self._backoff = 1.0

    # ── Event Loop ────────────────────────────────────────────────────────

    async def _event_loop(self) -> None:
        """Read messages from the WebSocket and handle them."""
        while not self._shutdown:
            try:
                raw = await self._ws.recv()
                data = json.loads(raw)
                await self._handle_message(data)
            except websockets.ConnectionClosed as e:
                self._log.warning(f"WebSocket closed: code={e.code}")
                await self._handle_disconnect(e.code)
                if self._shutdown:
                    return
                continue
            except asyncio.CancelledError:
                return
            except Exception as e:
                self._log.error(f"Event loop error: {e}")
                await self._handle_disconnect(None)
                if self._shutdown:
                    return

    async def _handle_message(self, data: dict) -> None:
        """Route a gateway message by opcode."""
        op = data.get(KEY_OP)

        if op == OP_DISPATCH:
            seq = data.get(KEY_SEQUENCE)
            if seq is not None:
                self._sequence = seq

            event_name = data.get(KEY_EVENT, "")
            payload = data.get(KEY_DATA, {})

            if event_name == "READY":
                self._handle_ready(payload)
            elif event_name == "GUILD_CREATE":
                self._handle_guild_create(payload)
            elif event_name == "RESUMED":
                self._log.info("Session resumed successfully")

            await self.dispatcher.dispatch(event_name, payload)

        elif op == OP_HEARTBEAT:
            await self._ws.send(json.dumps(build_heartbeat(self._sequence)))
            self._log.debug("Heartbeat sent (server-requested)")

        elif op == OP_HEARTBEAT_ACK:
            if self._heartbeat:
                self._heartbeat.ack()

        elif op == OP_RECONNECT:
            self._log.warning("Server requested reconnect (opcode 7)")
            await self._ws.close(4000)

        elif op == OP_INVALID_SESSION:
            resumable = data.get(KEY_DATA, False)
            self._log.warning(f"Invalid session (resumable={resumable})")
            if not resumable:
                self._session_id = None
                self._sequence = None
            await self._ws.close(4000)

        elif op == OP_GATEWAY_ERROR:
            error_data = data.get(KEY_DATA, {})
            self._log.error(f"Gateway error (opcode 12): {error_data}")

        else:
            self._log.debug(f"Unhandled opcode: {op}")

    def _handle_ready(self, payload: dict) -> None:
        """Process the READY event — extract session state."""
        self._session_id = payload.get("session_id")
        self.bot_user = payload.get("user", {})
        self.guilds = []

        bot_name = self.bot_user.get("username", "unknown")
        bot_id = self.bot_user.get("id", "?")

        self._log.success(f"Spooder connected as {bot_name} (ID: {bot_id})")
        self._log.info(
            f"Session: {self._session_id} | "
            f"Guilds arrive via GUILD_CREATE (lazy loading)"
        )

    def _handle_guild_create(self, payload: dict) -> None:
        """Track guilds as they arrive after READY."""
        guild_id = payload.get("id")
        guild_name = payload.get("name") or payload.get("id", "unknown")
        if guild_id and guild_id not in [g.get("id") for g in self.guilds]:
            self.guilds.append({"id": guild_id, "name": guild_name})
            self._log.info(
                f"Guild joined: {guild_name} (ID: {guild_id}) | "
                f"Total: {len(self.guilds)}"
            )

    # ── Reconnect ─────────────────────────────────────────────────────────

    async def _handle_disconnect(self, close_code: int | None) -> None:
        """Handle a WebSocket disconnect — resume or reconnect."""
        if self._shutdown:
            return

        if self._heartbeat:
            self._heartbeat.stop()

        if close_code and close_code in FATAL_CLOSE_CODES:
            raise NonRecoverableError(
                f"Fatal close code {close_code} — cannot reconnect"
            )

        can_resume = (
            self._session_id is not None
            and self._sequence is not None
            and close_code not in RE_IDENTIFY_CLOSE_CODES
        )

        await self._reconnect_loop(can_resume)

    async def _reconnect_loop(self, try_resume: bool) -> None:
        """Reconnect with exponential backoff."""
        attempts = 0

        while not self._shutdown:
            attempts += 1
            self._log.warning(
                f"Reconnecting (attempt {attempts}, "
                f"backoff {self._backoff:.1f}s, "
                f"resume={try_resume})..."
            )
            await asyncio.sleep(self._backoff)

            try:
                await self._connect(resume=try_resume)
                await self._event_loop()
                return
            except NonRecoverableError:
                raise
            except Exception as e:
                self._log.error(f"Reconnect attempt {attempts} failed: {e}")
                self._backoff = min(self._backoff * 2, self._max_backoff)

                if try_resume:
                    self._log.info("Resume failed — will try full re-identify")
                    try_resume = False
                    self._session_id = None
                    self._sequence = None

    # ── Cleanup ───────────────────────────────────────────────────────────

    async def _cleanup(self) -> None:
        """Clean up all connection resources."""
        if self._heartbeat:
            self._heartbeat.stop()
        if self._ws:
            try:
                await self._ws.close(1000)
            except Exception:
                pass
        self._log.info("Gateway resources cleaned up")

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def sequence(self) -> int | None:
        return self._sequence


# ── Factory function (Charter Rule #1) ────────────────────────────────────

def create_spooder_gateway(
    token: str, log, intents: int = INTENTS_ALL,
) -> SpooderGateway:
    """Factory function for SpooderGateway."""
    return SpooderGateway(token=token, log=log, intents=intents)


__all__ = ["SpooderGateway", "create_spooder_gateway", "NonRecoverableError"]
