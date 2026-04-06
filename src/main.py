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
FILE VERSION: v1.0.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

import asyncio
import signal
import sys

import httpx

from src.managers.config_manager import create_config_manager
from src.managers.logging_config_manager import create_logging_config_manager
from src.handlers.spooder_handler import create_spooder_handler

# TODO: Import the Fluxer gateway client library (fluxer-py or equivalent)
# from fluxer import Client, GatewayIntents


async def main() -> None:
    """Boot sequence: config → logging → http client → handler → gateway."""

    # ── 1. Static config ──────────────────────────────────────────────
    config = create_config_manager()

    # ── 2. Logging ────────────────────────────────────────────────────
    log_mgr = create_logging_config_manager(level=config.log_level)
    log = log_mgr.get_logger("spooder.main")
    log.info("Spooder is waking up...")

    # ── 3. HTTP client (shared for REST calls) ────────────────────────
    http_client = httpx.AsyncClient(
        headers={"Authorization": f"Bot {config.fluxer_token}"},
        timeout=httpx.Timeout(10.0),
    )

    # ── 4. Handler ────────────────────────────────────────────────────
    handler_log = log_mgr.get_logger("spooder.spooder_handler")
    handler = create_spooder_handler(
        config=config, http_client=http_client, log=handler_log,
    )

    log.success("Spooder handler ready")

    # ── 5. Gateway connection ─────────────────────────────────────────
    # TODO: Replace this placeholder with actual Fluxer gateway client.
    #
    # Example using fluxer-py (adjust to match the real library API):
    #
    #   client = Client(token=config.fluxer_token, intents=GatewayIntents.MESSAGES)
    #
    #   @client.on("MESSAGE_CREATE")
    #   async def on_message(payload: dict):
    #       await handler.handle_message(payload)
    #
    #   await client.start()
    #
    # For now, log a placeholder message so the boot sequence is testable.
    log.warning("Gateway client not yet wired — waiting for fluxer-py integration")
    log.info("Spooder is ready to spin webs! Waiting for gateway events...")

    # Keep the process alive until a signal is received
    stop_event = asyncio.Event()

    def _signal_handler() -> None:
        log.info("Shutdown signal received — Spooder is going to sleep...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _signal_handler)

    await stop_event.wait()

    # ── Graceful shutdown ─────────────────────────────────────────────
    log.info("Closing HTTP client...")
    await http_client.aclose()
    log.success("Spooder has gone to sleep. Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        sys.exit(1)
