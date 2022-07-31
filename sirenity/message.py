import json
from typing import Any


class Message:
    """Parses message"""

    action: str
    user_id: int
    token: str
    data: dict[str, list[str] | dict[str, int | str]]
    problem_id: int  # -1 for problem_id means that the message is not to do with a problem

    def __init__(self, message: str) -> None:
        """Assigns values"""
        message_dict = json.loads(message)
        self.action = message_dict.get("action")
        self.user_id = message_dict.get("user_id")
        self.token = message_dict.get("token")
        self.data = message_dict.get("data")
        self.problem_id = message_dict.get("problem_id")

    def __str__(self) -> str:
        """
        Returns string representation

        :return: string representation
        """
        return json.dumps(
            {
                "action": self.action,
                "user_id": self.user_id,
                "data": self.data,
                "problem_id": self.problem_id,
            }
        )


class JoinMessage:
    """Parses attributes to send to client"""

    action: str
    user_id: int
    token: str
    data: dict[str, Any]

    def __init__(
        self, action: str, user_id: int, token: str, data: dict[str, Any]
    ) -> None:
        """Assigns values"""
        self.action = action
        self.user_id = user_id
        self.token = token
        self.data = data

    def __str__(self) -> str:
        """
        Returns string representation

        :return: string representation
        """
        return json.dumps(
            {
                "action": self.action,
                "user_id": self.user_id,
                "token": self.token,
                "data": self.data,
            }
        )


class RequestCode:
    """Used to request code"""

    def __str__(self) -> str:
        """Returns string representation of data"""
        return json.dumps({"action": "request_code"})
