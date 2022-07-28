import os
import secrets

from fastapi import WebSocket

from .client import Client
from .euler import Problem, ProblemManager
from .message import Message

AMOUNT_OF_PROBLEMS = 5


class GameManager:
    """Manages the game"""

    def __init__(self, min_difficulty: int = 0, max_difficulty: int = 100):
        """
        Sets some attributes

        :param min_difficulty: the minimum difficulty of the problem
        :param max_difficulty: the maximum difficulty of the problem
        """
        self.clients: dict[int, Client] = {}
        self.current_id: int = 0
        self.questions: list[Problem] = []
        self.problem_manager: ProblemManager = ProblemManager(
            os.path.join(os.path.dirname(__file__), "db.db"),
            open(os.path.join(os.path.dirname(__file__), "euler.csv")),
        )
        self.problems = []
        while len(self.problems) < AMOUNT_OF_PROBLEMS:
            problem = self.problem_manager.get_random_problem(
                min_difficulty=min_difficulty, max_difficulty=max_difficulty
            )
            if problem not in self.problems:
                self.problems.append(problem)

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

    def get_problems(self) -> list[Problem]:
        """
        Returns a list of problems

        :returns: List of problems
        """
        return [problem.json() for problem in self.problems]
