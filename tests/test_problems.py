import sqlite3
import tempfile
import unittest
from typing import ClassVar

from sirenity.euler import Problem, ProblemManager, ProblemNotFoundError


class TestProblemManager(unittest.TestCase):
    """Tests ProblemManager"""

    manager: ClassVar[ProblemManager]
    database_location: ClassVar[str]

    def test_create_table(self) -> None:
        """Tests that table is in fact created"""
        connection = sqlite3.connect(self.database_location)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='problems';"
        )
        self.assertEqual(len(cursor.fetchall()), 1)
        connection.close()

    def test_add_and_get_problem(self) -> None:
        """Tests that problems are added and are retrieved"""
        problem = self.manager.get_at_id(1)
        self.assertEqual(problem.id, 1)
        self.assertEqual(problem.prompt, "Problem prompt")
        self.assertEqual(problem.solution, "solution")

    def test_get_error(self) -> None:
        """Tests that error is thrown if id is out of range"""
        with self.assertRaises(ProblemNotFoundError):
            self.manager.get_at_id(100)

    def test_check_solution(self) -> None:
        """Tests that the class returns the right boolean depending on if the solution is correct or not"""
        self.assertTrue(self.manager.check_solution("solution", 1))
        self.assertFalse(self.manager.check_solution("20933", 1))

    def test_check_random_problems(self) -> None:
        """Checks that random problems are returned and the difficulties are within the range"""
        min_difficulty, max_difficulty, number_of_problems = 30, 70, 5

        for i in range(10):
            self.manager.add_problem(
                Problem(
                    id=i * 10,
                    prompt="Problem prompt",
                    solution="solution",
                    difficulty=i * 10,
                )
            )
        self.assertTrue(isinstance(self.manager.get_random_problems()[0], Problem))

        self.assertTrue(
            self.manager.get_random_problems(min_difficulty=min_difficulty)[0].difficulty  # type: ignore
            >= min_difficulty
        )
        self.assertTrue(
            self.manager.get_random_problems(max_difficulty=max_difficulty)[0].difficulty  # type: ignore
            <= max_difficulty
        )
        self.assertTrue(
            min_difficulty  # type: ignore
            <= self.manager.get_random_problems(
                min_difficulty=min_difficulty, max_difficulty=max_difficulty
            )[0].difficulty
            <= max_difficulty
        )

        problems = self.manager.get_random_problems(
            number_of_problems=number_of_problems,
            min_difficulty=min_difficulty,
            max_difficulty=max_difficulty,
        )

        self.assertTrue(len(problems) == number_of_problems)

        for problem in problems:
            self.assertTrue(
                min_difficulty <= problem.difficulty <= max_difficulty  # type: ignore
            )

    @classmethod
    def setUpClass(cls):
        """Prepares tests"""
        file = tempfile.NamedTemporaryFile(suffix="db")
        file.close()

        cls.database_location = file.name
        cls.manager = ProblemManager(file.name)

        cls.manager.create_table()
        cls.manager.add_problem(
            Problem(id=1, prompt="Problem prompt", solution="solution", difficulty=1)
        )


if __name__ == "__main__":
    unittest.main()
