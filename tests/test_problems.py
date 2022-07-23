import sqlite3

import pytest

from sirenity.euler import ProblemManager
from sirenity.euler.problem import Problem

# Clear db
with open("test.db", "w") as f:
    f.write("")

manager = ProblemManager("test.db")


class TestClass:
    """Tests ProblemManager"""

    def test_create_table(self) -> None:
        """Tests that table is created"""
        con = sqlite3.connect(manager._file)
        cur = con.cursor()
        manager.create_table()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='problems';"
        )
        assert len(cur.fetchall()) == 1
        con.close()

    def test_add_and_get_problem(self) -> None:
        """Tests that problems are added and are retrieved"""
        manager.add_to_db(prompt="Problem prompt", solution="solution")
        problem = manager.get_at_id(1)
        assert problem.id == 1
        assert problem.prompt == "Problem prompt"
        assert problem.solution == "solution"

    def test_get_error(self) -> None:
        """Tests that error is thrown if id is out of range"""
        with pytest.raises(Exception):
            manager.get_at_id(2)

    def test_check_solution(self) -> None:
        """
        Tests that the class returns the right boolean
        depending on if the solution is correct or not
        """
        assert manager.check_solution("solution", 1) == True
        assert manager.check_solution("20933", 1) == False

    def test_check_random_problem(self) -> None:
        """Checks that a random problem is returned"""

        assert isinstance(manager.get_random_problem(), Problem)
