import json
from typing import NamedTuple


class Problem(NamedTuple):
    """Class that stores the data of the problem"""

    id: int
    prompt: str
    solution: str
    difficulty: int | None

    def json(self) -> str:
        """Returns the JSON representation of the problem, without the solution"""
        return json.dumps(
            {
                "id": self.id,
                "prompt": self.prompt,
                "difficulty": self.difficulty,
            }
        )

    @staticmethod
    def from_dictionary(dictionary: dict[str, int | str | None]) -> "Problem":
        """
        Returns a Problem from a dictionary

        :param dictionary: Dictionary with the values of the problem

        :return: Problem
        """
        if dictionary["id"] is None:
            raise Exception("ID not passed in")

        return Problem(
            id=int(dictionary["id"]),
            prompt=str(dictionary["prompt"]),
            difficulty=int(dictionary["difficulty"]),  # type: ignore
            solution=str(dictionary["solution"]),
        )
