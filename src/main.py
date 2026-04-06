"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================

MISSION:
    Give every chat a tiny spider friend that expresses emotions
    through ASCII art, one command at a time.

============================================================================
Application entrypoint. Connects to the Fluxer gateway, dispatches
MESSAGE_CREATE events to the spooder handler.
----------------------------------------------------------------------------
FILE VERSION: v1.1.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

import asyncio
import signal
import sys

from src.managers.config_manager import create_config_manager
from src.managers.logging_config_manager import create_logging_config_manager
from src.gateway import create_spooder_gateway, create_spooder_rest
from src.handlers.spooder_handler import create_spooder_handler


# ── Health server ─────────────────────────────────────────────────────────

async def _start_health_server(log) -> None:
    """Start a minimal HTTP health endpoint on port 8080."""

    async def _handle(reader, writer):
        await reader.read(1024)
        writer.write(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: 2\r\n\r\nOK"
        )
        await writer.drain()
        writer.close()

    server = await asyncio.start_server(_handle, "0.0.0.0", 8080)
    log.info("Health server listening on :8080")
    return server


async def main() -> None:
    """Boot sequence: config → logging → rest → handler → gateway."""

    # ── 1. Static config ──────────────────────────────────────────────
    config = create_config_manager()

    # ── 2. Logging ────────────────────────────────────────────────────
    log_mgr = create_logging_config_manager(level=config.log_level)
    log = log_mgr.get_logger("spooder.main")
    log.info("Spooder is waking up...")

    # ── 3. REST client ────────────────────────────────────────────────
    rest_log = log_mgr.get_logger("spooder.rest")
    rest = create_spooder_rest(token=config.fluxer_token, log=rest_log)

    # ── 4. Handler ────────────────────────────────────────────────────
    handler_log = log_mgr.get_logger("spooder.spooder_handler")
    handler = create_spooder_handler(
        config=config, rest=rest, log=handler_log,
    )
    log.success("Spooder handler ready")

    # ── 5. Health server ──────────────────────────────────────────────
    await _start_health_server(log_mgr.get_logger("spooder.health"))

    # ── 6. Gateway ────────────────────────────────────────────────────
    gw_log = log_mgr.get_logger("spooder.gateway")
    gateway = create_spooder_gateway(token=config.fluxer_token, log=gw_log)
    gateway.on("MESSAGE_CREATE", handler.handle_message)

    # ── 7. Signal handling ────────────────────────────────────────────
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(_shutdown(gateway, rest, log)),
        )

    # ── 8. Run gateway (blocks until shutdown) ────────────────────────
    log.info("Spooder is ready to spin webs!")
    await gateway.run()


async def _shutdown(gateway, rest, log) -> None:
    """Graceful shutdown sequence."""
    log.info("Shutdown signal received — Spooder is going to sleep...")
    await gateway.close()
    await rest.close()
    log.success("Spooder has gone to sleep. Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        sys.exit(1)
