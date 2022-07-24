import sqlite3
import tempfile
import unittest
from typing import ClassVar

from sirenity.euler import ProblemManager
from sirenity.euler.problem import Problem
from sirenity.euler.problems_manager import ProblemNotFoundError


class TestProblemManager(unittest.TestCase):
    """Tests ProblemManager"""

    manager: ClassVar[ProblemManager]

    def test_create_table(self) -> None:
        """Tests that table is created"""
        con = sqlite3.connect(self.manager._file)
        cur = con.cursor()
        self.manager.create_table()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='problems';"
        )
        self.assertEqual(len(cur.fetchall()), 1)
        con.close()

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

    def test_check_random_problem(self) -> None:
        """Checks that a random problem is returned and the difficulty is within the range"""
        min_difficulty, max_difficulty = 30, 70

        if self.manager.get_number_of_problems() == 0:
            with self.assertRaises(ProblemNotFoundError):
                self.manager.get_random_problem()
        for i in range(10):
            self.manager.add_to_db(
                prompt="Problem prompt", solution="solution", difficulty=i * 10
            )
        self.assertTrue(isinstance(self.manager.get_random_problem(), Problem))

        self.assertTrue(
            self.manager.get_random_problem(min_difficulty=min_difficulty).difficulty  # type: ignore
            >= min_difficulty
        )
        self.assertTrue(
            self.manager.get_random_problem(max_difficulty=max_difficulty).difficulty  # type: ignore
            <= max_difficulty
        )
        self.assertTrue(
            min_difficulty  # type: ignore
            <= self.manager.get_random_problem(
                min_difficulty=min_difficulty, max_difficulty=max_difficulty
            ).difficulty
            <= max_difficulty
        )

    @classmethod
    def setUpClass(cls):
        """Prepares tests"""
        file = tempfile.NamedTemporaryFile(suffix="db")
        file.close()
        cls.manager = ProblemManager(file.name)

        cls.manager.create_table()
        cls.manager.add_to_db(prompt="Problem prompt", solution="solution")


if __name__ == "__main__":
    unittest.main()
