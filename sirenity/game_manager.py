import asyncio
import json
import os
import secrets
import threading

from fastapi import WebSocket

from .client import Client
from .euler import Problem, ProblemManager
from .message import Message

AMOUNT_OF_PROBLEMS = 5
PARENT_DIR = os.path.dirname(__file__)
TIME_FOR_A_GAME = 30


class GameManager:
    """Manages the game"""

    def __init__(
        self,
        database: str = "problems.db",
        csv_file: str = "",
        min_difficulty: int = 0,
        max_difficulty: int = 100,
    ):
        """
        Sets some attributes

        :param min_difficulty: the minimum difficulty of the problem
        :param max_difficulty: the maximum difficulty of the problem
        """
        self.clients: dict[int, Client] = {}
        self.current_id: int = 0
        self.questions: list[Problem] = []
        self.database = database
        self.submitted_code: dict[int, dict[str, list[str]]] = {}
        self.started = False
        if csv_file:

            self.problem_manager: ProblemManager = ProblemManager(
                os.path.join(PARENT_DIR, database),
                open(os.path.join(PARENT_DIR, csv_file)),
            )
            self.csv_file = csv_file
        else:
            self.problem_manager = ProblemManager(
                os.path.join(PARENT_DIR, database),
            )
        self.problems: list[Problem] = []
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

    def get_problems(self) -> list[str]:
        """
        Returns a list of problems

        :returns: List of problems
        """
        return [problem.json() for problem in self.problems]

    def start(self) -> None:
        """Starts the game"""
        if not self.started:
            timer = threading.Timer(
                TIME_FOR_A_GAME, function=asyncio.run, args=(self.game_end(),)
            )
            timer.start()
            self.started = True

    def get_code(self, data: Message) -> dict[int, str] | None:
        """
        Gets code from clients

        :param data: Message from the clients

        :returns: Code to be run
        """
        if data.user_id in self.submitted_code.keys():
            return
        if not secrets.compare_digest(self.clients[data.user_id].token, data.token):
            return
        self.submitted_code[data.user_id] = data.data["code"]

        code_variations: dict[int, dict[str, int]] = {
            problem.id: {} for problem in self.problems
        }
        if len(self.submitted_code) == len(self.clients):
            # Loop below to check which version of the code is the most common.
            # This prevents getting the wrong code from one person because they
            # have a high ping or something.
            for solutions in self.submitted_code.values():
                for problem_id, solution in solutions.items():
                    solution = "\n".join(solution)
                    if code_variations[int(problem_id)].get(solution):
                        code_variations[int(problem_id)][solution] += 1
                    else:
                        code_variations[int(problem_id)][solution] = 1

            code_to_return: dict[int, str] = {}
            for problem_id, variations in code_variations.items():
                code_to_return[problem_id] = sorted(
                    variations.items(), key=lambda variation: variation[1], reverse=True
                )[0][0]

            return code_to_return

    async def game_end(self) -> None:
        """Signals to clients to submit code"""
        for client in self.clients.values():
            await client.websocket.send_text(
                str(
                    Message(
                        json.dumps(
                            {
                                "action": "game_end",
                            }
                        )
                    )
                )
            )
