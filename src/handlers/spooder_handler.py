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
FILE VERSION: v1.0.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

import time

import httpx

from src.utils.emotions import build_spider, get_eyes, list_emotions


FLUXER_API = "https://api.fluxer.chat/v1"  # TODO: confirm Fluxer REST base URL


class SpooderHandler:
    """Handles !spooder commands — parses, deletes, renders."""

    def __init__(self, config, http_client: httpx.AsyncClient, log) -> None:
        self._config = config
        self._http = http_client
        self._log = log
        self._recent_events: dict[str, float] = {}
        self._dedup_window: float = 5.0

    # ------------------------------------------------------------------
    # Dedup guard — Fluxer fires gateway events twice
    # ------------------------------------------------------------------
    def _is_duplicate(self, key: str) -> bool:
        now = time.monotonic()
        last = self._recent_events.get(key, 0.0)
        if now - last < self._dedup_window:
            return True
        self._recent_events[key] = now
        return False

    # ------------------------------------------------------------------
    # REST helpers
    # ------------------------------------------------------------------
    async def _delete_message(self, channel_id: str, message_id: str) -> bool:
        """Attempt to delete the command message. Returns True on success."""
        try:
            resp = await self._http.delete(
                f"{FLUXER_API}/channels/{channel_id}/messages/{message_id}",
            )
            if resp.status_code == 204:
                return True
            self._log.warning(
                f"Message delete returned {resp.status_code} for {message_id}"
            )
            return False
        except Exception as exc:
            self._log.warning(f"Failed to delete message {message_id}: {exc}")
            return False

    async def _send_message(self, channel_id: str, content: str) -> None:
        """Post a message to the given channel."""
        try:
            resp = await self._http.post(
                f"{FLUXER_API}/channels/{channel_id}/messages",
                json={"content": content},
            )
            if resp.status_code not in (200, 201):
                self._log.error(
                    f"Send message failed ({resp.status_code}): {resp.text}"
                )
        except Exception as exc:
            self._log.error(f"Failed to send message to {channel_id}: {exc}")

    # ------------------------------------------------------------------
    # Main handler
    # ------------------------------------------------------------------
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
        args = content[len(prefix):].strip()

        # Parse: <emotion> [message...]
        if not args:
            # No arguments — show help
            help_text = list_emotions()
            await self._send_message(channel_id, f"```\n{help_text}\n```")
            return

        parts = args.split(None, 1)
        emotion = parts[0].lower()
        message = parts[1] if len(parts) > 1 else None

        # Look up the emotion
        eyes = get_eyes(emotion)
        if eyes is None:
            help_text = list_emotions()
            await self._send_message(
                channel_id,
                f"Unknown emotion: `{emotion}`\n```\n{help_text}\n```",
            )
            return

        # Build the spider output
        spider_output = build_spider(eyes, message)

        # Delete the command message first, then post the spider
        await self._delete_message(channel_id, message_id)
        await self._send_message(channel_id, spider_output)

        self._log.debug(f"Rendered spider: {emotion} in {channel_id}")


def create_spooder_handler(config, http_client: httpx.AsyncClient, log) -> SpooderHandler:
    """Factory function for SpooderHandler."""
    return SpooderHandler(config=config, http_client=http_client, log=log)


__all__ = ["SpooderHandler", "create_spooder_handler"]
