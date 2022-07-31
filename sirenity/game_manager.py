import asyncio
import json
import os
import random
import secrets
import threading

from fastapi import WebSocket

from .client import Client
from .euler import Problem, ProblemManager
from .message import Message, RequestCode

AMOUNT_OF_PROBLEMS = 10
PARENT_DIR = os.path.dirname(__file__)
PEOPLE_PER_GAME = 1
TIME_FOR_A_GAME = 10


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
        self.waiting_for_code_request = False
        self.game_ended = False
        self.votes: dict[int, int] = {}
        self.voted: list[int] = []
        self.clients_waiting_for_code: set[WebSocket] = set()
        self.bugposter: Client | None = None
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

    async def broadcast(
        self, client_id: int, message: Message, *, server: bool = False
    ) -> None:
        """
        Broadcasts message to rest of clients

        :param client_id: ID of the client sending the message
        :param message: Message to broadcast
        :param server: If it's the server broadcasting
        """
        if not server:
            if not secrets.compare_digest(self.clients[client_id].token, message.token):
                return
            del message.token
        for id_, client in self.clients.items():
            if client_id == id_ and message.action != "chat_message" and not server:
                continue
            try:
                await client.websocket.send_text(str(message))
            except RuntimeError:  # Client left or reloaded
                pass

    async def add_client(self, websocket: WebSocket) -> tuple[int, str]:
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
        self.votes[self.current_id] = 0
        if len(self.clients) == PEOPLE_PER_GAME:
            self.bugposter = random.choice(list(self.clients.values()))
            await self.bugposter.websocket.send_text(
                str(
                    Message(
                        json.dumps({"action": "role", "data": {"role": "Bugposter"}})
                    )
                )
            )
            for client in self.clients.values():
                if self.bugposter == client:
                    continue
                await client.websocket.send_text(
                    str(
                        Message(
                            json.dumps(
                                {"action": "role", "data": {"role": "Code Mate"}}
                            )
                        )
                    )
                )

            self.start()
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
            return None
        if not secrets.compare_digest(self.clients[data.user_id].token, data.token):
            return None
        self.submitted_code[data.user_id] = data.data["code"]  # type: ignore

        code_variations: dict[int, dict[str, int]] = {
            problem.id: {} for problem in self.problems
        }
        if len(self.submitted_code) == len(self.clients):
            # Loop below to check which version of the code is the most common.
            # This prevents getting the wrong code from one person because they
            # have a high ping or something.
            for solutions in self.submitted_code.values():
                for problem_id, solution in solutions.items():
                    solution_str = "\n".join(solution)
                    if code_variations[int(problem_id)].get(solution_str):
                        code_variations[int(problem_id)][solution_str] += 1
                    else:
                        code_variations[int(problem_id)][solution_str] = 1

            code_to_return: dict[int, str] = {}
            for problem_id, variations in code_variations.items():  # type: ignore
                code_to_return[int(problem_id)] = sorted(
                    variations.items(), key=lambda variation: variation[1], reverse=True
                )[0][0]

            return code_to_return
        return None

    async def game_end(self) -> None:
        """Signals to clients to submit code"""
        for client in self.clients.values():
            await client.websocket.send_text(
                str(
                    Message(
                        json.dumps(
                            {
                                "action": "game_end",
                                "data": {"users": list(self.clients.keys())},
                            }
                        )
                    )
                )
            )
        self.game_ended = True

    async def request_code(self, websocket: WebSocket) -> None:
        """
        Request code so a late joining or reloading client can have the code

        :param websocket: Client requesting the code
        """
        if not self.waiting_for_code_request:
            self.first_client = list(self.clients.values())[0].websocket
            await self.first_client.send_text(str(RequestCode()))
            self.waiting_for_code_request = True
        self.clients_waiting_for_code.add(websocket)

    async def send_requested_code(self, data: Message) -> None:
        """
        Sends requested code to clients

        :param data: Message
        """
        for websocket in self.clients_waiting_for_code.copy():
            try:
                await websocket.send_text(str(data))
            except RuntimeError:  # Client left or reloaded
                pass
            self.clients_waiting_for_code.remove(websocket)

    async def vote(self, data: Message) -> None:
        """
        Handles voting

        :param data: Message
        """
        if not secrets.compare_digest(self.clients[data.user_id].token, data.token):
            return

        if data.user_id in self.voted:
            return
        self.votes[int(data.data["voted"])] += 1  # type: ignore
        self.voted.append(data.user_id)
        if len(self.voted) == PEOPLE_PER_GAME:
            highest_voted = sorted(
                self.votes.items(), key=lambda vote: vote[1], reverse=True
            )

            # If there is a tie or they voted wrong
            if len(highest_voted) > 1:
                if (
                    highest_voted[0][1] == highest_voted[1][1]
                    or self.clients[highest_voted[0][0]] != self.bugposter
                ):
                    await self.broadcast(
                        -1,
                        Message(
                            json.dumps(
                                {
                                    "action": "result",
                                    "data": {
                                        "result": "lost",
                                        "bugposter": self.bugposter.id,  # type: ignore
                                    },
                                }
                            )
                        ),
                        server=True,
                    )
                    return
                await self.broadcast(
                    -1,
                    Message(
                        json.dumps(
                            {
                                "action": "result",
                                "data": {
                                    "result": "won",
                                    "bugposter": self.bugposter.id,
                                },
                            }
                        )
                    ),
                    server=True,
                )
