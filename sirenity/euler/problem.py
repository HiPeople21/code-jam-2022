from typing import NamedTuple


class Problem(NamedTuple):
    """Class that stores the data of the problem"""

    id: int
    prompt: str
    solution: str
    difficulty: int | None
