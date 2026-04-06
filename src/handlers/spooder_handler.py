"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================

MISSION:
    Give every chat a tiny spider friend that expresses emotions
    through ASCII art, one command at a time.

============================================================================
Spooder command handler. Parses !spooder commands, deletes the original
message, and posts the rendered spider with the user's message.
----------------------------------------------------------------------------
FILE VERSION: v1.2.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

import time

from src.gateway.rest import SpooderREST
from src.utils.emotions import build_spider, get_eyes, list_emotions


class SpooderHandler:
    """Handles !spooder commands — parses, deletes, renders."""

    def __init__(self, config, rest: SpooderREST, log) -> None:
        self._config = config
        self._rest = rest
        self._log = log
        self._recent_events: dict[str, float] = {}
        self._dedup_window: float = 5.0

    # ── Dedup guard (Charter Rule #7) ─────────────────────────────────

    def _is_duplicate(self, key: str) -> bool:
        now = time.monotonic()
        last = self._recent_events.get(key, 0.0)
        if now - last < self._dedup_window:
            return True
        self._recent_events[key] = now
        return False

    # ── Main handler ──────────────────────────────────────────────────

    async def handle_message(self, payload: dict) -> None:
        """Process an incoming MESSAGE_CREATE event."""
        # Ignore bot messages
        author = payload.get("author", {})
        if author.get("bot", False):
            return

        content: str = payload.get("content", "").strip()
        prefix = self._config.command_prefix

        # Only respond to our command
        if not content.startswith(prefix):
            return

        # Dedup guard
        author_id = author.get("id", "")
        message_id = payload.get("id", "")
        dedup_key = f"{author_id}:{message_id}"
        if self._is_duplicate(dedup_key):
            return

        channel_id = payload.get("channel_id", "")

        # ── Access control ────────────────────────────────────────────
        # Allow if: user is the configured owner, OR has Administrator
        # permission (0x8 bit) in their guild member permissions.
        is_owner = (
            self._config.owner_user_id
            and str(author_id) == self._config.owner_user_id
        )
        member = payload.get("member", {})
        perms = int(member.get("permissions", 0))
        is_admin = bool(perms & 0x8)

        if not is_owner and not is_admin:
            return  # Silent ignore — unauthorized user

        args = content[len(prefix):].strip()

        # No arguments — show help
        if not args:
            help_text = list_emotions()
            await self._rest.send_message(
                channel_id, content=f"```\n{help_text}\n```",
            )
            return

        parts = args.split(None, 1)
        emotion = parts[0].lower()
        message = parts[1] if len(parts) > 1 else None

        # Look up the emotion
        eyes = get_eyes(emotion)
        if eyes is None:
            help_text = list_emotions()
            await self._rest.send_message(
                channel_id,
                content=f"Unknown emotion: `{emotion}`\n```\n{help_text}\n```",
            )
            return

        # Build the spider output
        spider_output = build_spider(eyes, message)

        # Delete the command message first, then post the spider
        await self._rest.delete_message(channel_id, message_id)
        await self._rest.send_message(channel_id, content=spider_output)

        self._log.debug(f"Rendered spider: {emotion} in {channel_id}")


def create_spooder_handler(
    config, rest: SpooderREST, log,
) -> SpooderHandler:
    """Factory function for SpooderHandler."""
    return SpooderHandler(config=config, rest=rest, log=log)


__all__ = ["SpooderHandler", "create_spooder_handler"]
