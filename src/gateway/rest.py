"""
============================================================================
Spooder — Emotive Spider Bot for Fluxer
The Alphabet Cartel
============================================================================
SpooderREST — REST API helpers for Fluxer operations.
Thin wrappers around httpx. All methods return None or False on failure
(logged at WARNING). No exceptions propagate to handlers.
----------------------------------------------------------------------------
FILE VERSION: v1.0.0
LAST MODIFIED: 2026-04-05
COMPONENT: spooder
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/PapaBearDoes/spooder
============================================================================
"""

import httpx

from src.gateway.constants import API_BASE


class SpooderREST:
    """REST API helpers for Fluxer operations.

    Provides only the methods Spooder needs: send messages and
    delete messages.
    """

    def __init__(self, token: str, log) -> None:
        self._token = token
        self._log = log
        self._client = httpx.AsyncClient(
            base_url=API_BASE,
            headers={"Authorization": f"Bot {token}"},
            timeout=15.0,
            limits=httpx.Limits(
                max_connections=10,
                max_keepalive_connections=5,
                keepalive_expiry=30.0,
            ),
        )

    # ── Send Message ──────────────────────────────────────────────────────

    async def send_message(
        self, channel_id: int | str, *, content: str,
    ) -> dict | None:
        """POST /channels/{id}/messages — send a message."""
        try:
            resp = await self._client.post(
                f"/channels/{channel_id}/messages",
                json={"content": content},
            )
            if resp.status_code in (200, 201):
                return resp.json()
            self._log.warning(
                f"send_message({channel_id}): HTTP {resp.status_code} "
                f"{resp.text[:200]}"
            )
        except Exception as e:
            self._log.warning(f"send_message({channel_id}): {e}")
        return None

    # ── Delete Message ────────────────────────────────────────────────────

    async def delete_message(
        self, channel_id: int | str, message_id: int | str,
    ) -> bool:
        """DELETE /channels/{id}/messages/{id} — delete a message.

        Returns True on success, False on failure.
        """
        try:
            resp = await self._client.delete(
                f"/channels/{channel_id}/messages/{message_id}",
            )
            if resp.status_code == 204:
                return True
            self._log.warning(
                f"delete_message({channel_id}/{message_id}): "
                f"HTTP {resp.status_code}"
            )
        except Exception as e:
            self._log.warning(
                f"delete_message({channel_id}/{message_id}): {e}"
            )
        return False

    # ── Lifecycle ─────────────────────────────────────────────────────────

    async def close(self) -> None:
        """Close the underlying httpx client."""
        await self._client.aclose()

    @property
    def token(self) -> str:
        return self._token


# ── Factory function (Charter Rule #1) ────────────────────────────────────

def create_spooder_rest(token: str, log) -> SpooderREST:
    """Factory function for SpooderREST."""
    return SpooderREST(token=token, log=log)


__all__ = ["SpooderREST", "create_spooder_rest"]
