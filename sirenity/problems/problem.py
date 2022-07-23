from dataclasses import dataclass


@dataclass(slots=True)
class Problem:
    """Class that stores the data of the problem"""

    id: int
    prompt: str
    solution: str
