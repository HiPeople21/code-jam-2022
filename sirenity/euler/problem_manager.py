import asyncio
import csv
from typing import TextIO

import aiosqlite

from .problem import Problem

__all__ = ["ProblemNotFoundError", "ProblemManager"]


class ProblemNotFoundError(Exception):
    """Thrown when problem is not found"""

    pass


class ProblemManager:
    """Manages changes in database"""

    _connection: aiosqlite.Connection
    _cursor: aiosqlite.Cursor

    @staticmethod
    async def create(
        database_location: str, sourcefile: TextIO = None
    ) -> "ProblemManager":
        """
        Asynchronously sets up class

        :param file: Database file
        :param sourcefile: Source file
        """
        self = ProblemManager()
        self._connection = await aiosqlite.connect(database_location)
        self._cursor = await self._connection.cursor()
        await self.create_table()

        if sourcefile:
            await self.load_problems(sourcefile)
        return self

    async def create_table(self) -> None:
        """
        Creates problems table if it does not exist

        :return: None
        """
        await self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER NOT NULL PRIMARY KEY,
                prompt TEXT NOT NULL,
                solution TEXT NOT NULL,
                difficulty INTEGER
            );
            """
        )

        await self._connection.commit()

    async def add_problem(self, problem: Problem) -> None:
        """
        Adds a problem to database

        :param prompt: Question prompt
        :param solution: Solution of the problem

        :return: None
        """
        await self._cursor.execute(
            """
            INSERT INTO problems (id, prompt, solution, difficulty)
            VALUES (?, ?, ?, ?)
            """,
            (problem.id, problem.prompt, problem.solution, problem.difficulty),
        )

        await self._connection.commit()

    async def get_at_id(self, id: int) -> Problem:
        """
        Gets a problem by id

        :param id: id of problem

        :return: Problem
        """
        await self._cursor.execute(
            """
            SELECT id, prompt, solution, difficulty FROM problems
            WHERE id = ?;
            """,
            (id,),
        )

        row = await self._cursor.fetchone()
        if row is None:
            raise ProblemNotFoundError(f"Problem of id {id} does not exist")
        problem = Problem(row[0], row[1], row[2], row[3])
        return problem

    async def check_solution(self, value: str, id: int) -> bool:
        """
        Checks if solution is correct

        :param value: value returned by the program written by the user
        :param id: id of the problem
        :return: True if solution is correct
        """
        return (await self.get_at_id(id)).solution == value

    async def get_number_of_problems(self) -> int:
        """
        Returns number of rows in table

        :return: number of rows in table
        """
        await self._cursor.execute(
            """
            SELECT COUNT(*) FROM problems;
            """,
        )

        return await self._cursor.fetchone()[0]  # type: ignore

    async def get_random_problems(
        self,
        number_of_problems: int = 1,
        *,
        min_difficulty: int = 0,
        max_difficulty: int = 100,
    ) -> list[Problem]:
        """
        Returns random problems

        :param number_of_problems: number of problems to be returned
        :param min_difficulty: Minimum difficulty of the problem
        :param max_difficulty:Maximum difficulty of the problem
        :return: random problems
        """
        await self._cursor.execute(
            """
            SELECT id, prompt, solution, difficulty FROM problems
            WHERE difficulty BETWEEN ? AND ?
            ORDER BY RANDOM() LIMIT ?;
            """,
            (min_difficulty, max_difficulty, number_of_problems),
        )

        rows: list[tuple[int, str, str, int]] = await self._cursor.fetchall()  # type: ignore
        if len(rows) < number_of_problems:
            raise ProblemNotFoundError("Not enough problems can be found")

        return [Problem(*row) for row in rows]

    async def load_problems(self, source_file):
        """Adds problems to the database"""
        reader = csv.DictReader(source_file)

        for row in reader:
            await self.add_problem(Problem.from_dictionary(row))

    def __del__(self):
        """Closes databse connection"""
        try:
            asyncio.get_running_loop().create_task(self._connection.close())
        except RuntimeError:
            asyncio.run(self._connection.close())


async def main():
    a = await ProblemManager.create("problems.db")
    await a.get_random_problems(4)


if __name__ == "__main__":
    asyncio.run(main())
