import os
import sqlite3
import unittest

from sirenity.euler import ProblemManager
from sirenity.euler.problem import Problem
from sirenity.euler.problems_manager import NotFoundError


class TestProblemManager(unittest.TestCase):
    """Tests ProblemManager"""

    def __init__(self, *args, **kwargs):
        """Prepares for tests"""
        super().__init__(*args, **kwargs)
        if not os.path.exists("test.db"):
            with open("test.db", "w"):
                pass

        # Clear db
        with open("test.db", "w") as f:
            f.write("")

        self.manager = ProblemManager("test.db")
        self.manager.create_table()

    def test_create_table(self) -> None:
        """Tests that table is created"""
        con = sqlite3.connect(self.manager._file)
        cur = con.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='problems';"
        )
        self.assertEqual(len(cur.fetchall()), 1)
        con.close()

    def test_add_and_get_problem(self) -> None:
        """Tests that problems are added and are retrieved"""
        self.manager.add_to_db(prompt="Problem prompt", solution="solution")
        problem = self.manager.get_at_id(1)
        self.assertEqual(problem.id, 1)
        self.assertEqual(problem.prompt, "Problem prompt")
        self.assertEqual(problem.solution, "solution")

    def test_get_error(self) -> None:
        """Tests that error is thrown if id is out of range"""
        with self.assertRaises(NotFoundError):
            self.manager.get_at_id(2)

    def test_check_solution(self) -> None:
        """
        Tests that the class returns the right boolean
        depending on if the solution is correct or not
        """
        self.assertTrue(self.manager.check_solution("solution", 1))
        self.assertFalse(self.manager.check_solution("20933", 1))

    def test_check_random_problem(self) -> None:
        """Checks that a random problem is returned"""
        self.assertTrue(isinstance(self.manager.get_random_problem(), Problem))


if __name__ == "__main__":
    unittest.main()
