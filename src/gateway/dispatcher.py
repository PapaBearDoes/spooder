"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================
Gateway event dispatcher — multi-handler event registry and dispatch.
Handlers fire in registration order. A failure in one handler does not
prevent subsequent handlers from running.
----------------------------------------------------------------------------
FILE VERSION: v1.0.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

import traceback
from collections import defaultdict
from typing import Callable, Awaitable


class SpooderDispatcher:
    """Multi-handler event dispatch registry."""

    def __init__(self, log) -> None:
        self._handlers: dict[str, list[Callable]] = defaultdict(list)
        self._log = log

    def on(self, event_name: str, handler: Callable[..., Awaitable]) -> None:
        """Register a handler for a gateway event."""
        self._handlers[event_name].append(handler)
        self._log.debug(
            f"Registered handler for {event_name} "
            f"({len(self._handlers[event_name])} total)"
        )

    async def dispatch(self, event_name: str, payload: dict) -> None:
        """Dispatch an event to all registered handlers.

        Each handler is called sequentially. A failure in one does not
        prevent subsequent handlers from running.
        """
        handlers = self._handlers.get(event_name)
        if not handlers:
            return

        for handler in handlers:
            try:
                await handler(payload)
            except Exception as e:
                self._log.error(
                    f"Handler error for {event_name}: {e}\n"
                    f"{traceback.format_exc()}"
                )

    @property
    def registered_events(self) -> list[str]:
        return list(self._handlers.keys())


__all__ = ["SpooderDispatcher"]
