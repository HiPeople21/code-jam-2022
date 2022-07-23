from problem import Problem
import sqlite3


class ProblemManager:
    """Manages changes in database"""

    def __init__(self, file: str = "problems.db"):
        """
        Sets attributes for handling problems

        :param file: Database file
        """
        self._file = file
        self._con = sqlite3.connect(self._file)
        self._cur = self._con.cursor()

    def create_table(self) -> None:
        """
        Creates problems table if it does not exist

        :return: None
        """

        self._cur.execute(
            """
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER NOT NULL PRIMARY KEY,
                prompt TEXT NOT NULL,
                solution TEXT NOT NULL
            );
            """
        )

        self._con.commit()

    def add_to_db(self, prompt: str, solution: str, id: int | None = None) -> None:
        """
        Adds problem to database

        :param prompt: Question prompt
        :param solution: Solution of the problem

        :return: None
        """
        if id is None:
            self._cur.execute(
                """
                INSERT INTO problems (prompt, solution)
                VALUES (?,?)
                """,
                (prompt, solution),
            )
        elif id is not None:
            self._cur.execute(
                """
                INSERT INTO problems (id, prompt, solution)
                VALUES (?,?,?)
                """,
                (id, prompt, solution),
            )

        self._con.commit()

    def get_at_id(self, id: int) -> Problem:
        """
        Gets a problem by id

        :param id: id of problem

        :return: Problem
        """
        self._cur.execute(
            """
            SELECT id, prompt, solution FROM problems
            WHERE id = ?;
            """,
            (id,),
        )

        row = self._cur.fetchone()
        if row is None:
            raise Exception(f"Problem of id {id} does not exist")
        problem = Problem(row[0], row[1], row[2])
        return problem
    
    def check_solution(self, value:str, id:int) -> bool:
        return self.get_at_id(id).solution == value


if __name__ == "__main__":
    import os

    def add_problems():
        manager = ProblemManager()
        manager.create_table()
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "sources/prompts.txt")
        with open(filename, "r", encoding="utf-8") as f:
            prompts = f.read().split("==========")
        filename = os.path.join(dirname, "sources/solutions.txt")
        with open(filename, "r", encoding="utf-8") as f:
            solutions = f.read().splitlines()[: len(prompts)]
        qs = zip(prompts, solutions)
        for index, q in enumerate(qs, 1):
            manager.add_to_db(q[0], q[1], index)
