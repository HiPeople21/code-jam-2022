from dataclasses import dataclass

from fastapi import WebSocket


@dataclass(slots=True)
class Client:
    """Holds client data"""

    id: int
    token: str
    websocket: WebSocket
