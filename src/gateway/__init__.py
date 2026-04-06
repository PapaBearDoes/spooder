"""
Spooder gateway package — native Fluxer WebSocket client.
Adapted from Fluxarr's gateway implementation.
"""

from src.gateway.client import (
    SpooderGateway,
    create_spooder_gateway,
    NonRecoverableError,
)
from src.gateway.rest import SpooderREST, create_spooder_rest
from src.gateway.dispatcher import SpooderDispatcher

__all__ = [
    "SpooderGateway",
    "create_spooder_gateway",
    "NonRecoverableError",
    "SpooderREST",
    "create_spooder_rest",
    "SpooderDispatcher",
]
