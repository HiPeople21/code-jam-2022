import sqlite3

import pytest

from sirenity.problems import ProblemManager

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
