import csv
import sqlite3
from typing import TextIO

from .problem import Problem

__all__ = ["ProblemNotFoundError", "ProblemManager"]


class ProblemNotFoundError(Exception):
    """Thrown when problem is not found"""

    pass


class ProblemManager:
    """Manages changes in database"""

    def __init__(self, database_location: str, sourcefile: TextIO | None = None):
        """
        Sets attributes for handling problems

        :param file: Database file
        """
        self._connection = sqlite3.connect(database_location)
        self._cursor = self._connection.cursor()

        self.create_table()

        if sourcefile:
            self.load_problems(sourcefile)

    def create_table(self) -> None:
        """
        Creates problems table if it does not exist

        :return: None
        """
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER NOT NULL PRIMARY KEY,
                prompt TEXT NOT NULL,
                solution TEXT NOT NULL,
                difficulty INTEGER
            );
            """
        )

        self._connection.commit()

    def add_problem(self, problem: Problem) -> None:
        """
        Adds a problem to database

        :param prompt: Question prompt
        :param solution: Solution of the problem

        :return: None
        """
        self._cursor.execute(
            """
            INSERT INTO problems (id, prompt, solution, difficulty)
            VALUES (?, ?, ?, ?)
            """,
            (problem.id, problem.prompt, problem.solution, problem.difficulty),
        )

        self._connection.commit()

    def get_at_id(self, id: int) -> Problem:
        """
        Gets a problem by id

        :param id: id of problem

        :return: Problem
        """
        self._cursor.execute(
            """
            SELECT id, prompt, solution, difficulty FROM problems
            WHERE id = ?;
            """,
            (id,),
        )

        row = self._cursor.fetchone()
        if row is None:
            raise ProblemNotFoundError(f"Problem of id {id} does not exist")
        problem = Problem(row[0], row[1], row[2], row[3])
        return problem

    def check_solution(self, value: str, id: int) -> bool:
        """
        Checks if solution is correct

        :param value: value returned by the program written by the user
        :param id: id of the problem
        :return: True if solution is correct
        """
        return self.get_at_id(id).solution == value

    def get_number_of_problems(self) -> int:
        """
        Returns number of rows in table

        :return: number of rows in table
        """
        self._cursor.execute(
            """
            SELECT COUNT(*) FROM problems;
            """,
        )

        return self._cursor.fetchone()[0]

    def get_random_problem(
        self, *, min_difficulty: int = 0, max_difficulty: int = 100
    ) -> Problem:
        """
        Returns a random problem

        :param min_difficulty: Minimum difficulty of the problem
        :param max_difficulty:Maximum difficulty of the problem
        :return: random problem
        """
        self._cursor.execute(
            """
            SELECT id, prompt, solution, difficulty FROM problems
            WHERE difficulty BETWEEN ? AND ?
            ORDER BY RANDOM() LIMIT 1;
            """,
            (min_difficulty, max_difficulty),
        )

        row = self._cursor.fetchone()
        if row is None:
            raise ProblemNotFoundError("No problems can be found")

        return Problem(*row)

    def load_problems(self, source_file: TextIO | None):
        """Adds problems to the database"""
        reader = csv.DictReader(source_file)

        for row in reader:
            self.add_problem(Problem.from_dictionary(row))

    # def __del__(self):
    #     self._connection.close()
