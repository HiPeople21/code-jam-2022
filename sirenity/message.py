import json


class Message:
    """Parses message"""

    action: str
    user_id: int
    token: str
    data: dict[str, list[str] | dict[str, int]]
    problem_id: int

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
