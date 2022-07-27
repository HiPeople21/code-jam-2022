import secrets

from fastapi import WebSocket

from .client import Client
from .message import Message


class GameManager:
    """Manages the game"""

    def __init__(self):
        """Sets some attributes"""
        self.clients: dict[int, Client] = {}
        self.current_id = 0

    async def broadcast(self, client_id: int, message: Message) -> None:
        """
        Broadcasts message to rest of clients

        :param client_id: ID of the client sending the message
        :message: Message to broadcast
        """
        if not secrets.compare_digest(self.clients[client_id].token, message.token):
            return
        del message.token
        for id_, client in self.clients.items():
            if client_id == id_:
                continue
            await client.websocket.send_text(str(message))

    def add_client(self, websocket: WebSocket) -> tuple[int, str]:
        """
        Adds client

        :param websocket: Client websocket

        :returns: ID of the client and token
        """
        token = secrets.token_hex(32)
        self.current_id += 1
        self.clients[self.current_id] = Client(
            id=self.current_id, websocket=websocket, token=token
        )
        return self.current_id, token

    def remove_client(self, user_id: int) -> None:
        """
        Removes client

        :param user_id: Client ID
        """
        del self.clients[user_id]
