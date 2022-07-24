import os
import sqlite3

from .problem import Problem


class ProblemNotFoundError(Exception):
    """Thrown when problem is not found"""

    pass


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
                solution TEXT NOT NULL,
                difficulty INTEGER
            );
            """
        )

        self._con.commit()

    def add_to_db(
        self,
        prompt: str,
        solution: str,
        difficulty: int | None = None,
        id: int | None = None,
    ) -> None:
        """
        Adds problem to database

        :param prompt: Question prompt
        :param solution: Solution of the problem

        :return: None
        """
        if id is None:
            self._cur.execute(
                """
                INSERT INTO problems (prompt, solution, difficulty)
                VALUES (?,?,?)
                """,
                (prompt, solution, difficulty),
            )
        elif id is not None:
            self._cur.execute(
                """
                INSERT INTO problems (id, prompt, solution, difficulty)
                VALUES (?,?,?,?)
                """,
                (id, prompt, solution, difficulty),
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
            SELECT id, prompt, solution, difficulty FROM problems
            WHERE id = ?;
            """,
            (id,),
        )

        row = self._cur.fetchone()
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
        self._cur.execute(
            """
            SELECT COUNT(*) FROM problems;
            """,
        )

        return self._cur.fetchone()[0]

    def get_random_problem(
        self, *, min_difficulty: int = 0, max_difficulty: int = 100
    ) -> Problem:
        """
        Returns a random problem

        :param min_difficulty: Minimum difficulty of the problem
        :param max_difficulty:Maximum difficulty of the problem
        :return: random problem
        """
        self._cur.execute(
            """
            SELECT id, prompt, solution, difficulty FROM problems
            WHERE difficulty BETWEEN ? AND ?
            ORDER BY RANDOM() LIMIT 1;
            """,
            (min_difficulty, max_difficulty),
        )

        row = self._cur.fetchone()
        if row is None:
            raise ProblemNotFoundError("No problems can be found")

        return Problem(row[0], row[1], row[2], row[3])


def add_problems():
    """Adds problems to the database"""
    manager = ProblemManager()
    manager.create_table()
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "sources/prompts.txt")

    questions = []
    with open(filename, "r", encoding="utf-8") as file:
        prompts = file.read().split("==========")

        for prompt in prompts:
            prompt, difficulty = prompt.strip().split("----------")
            if difficulty.strip().startswith("Solved by "):
                difficulty = None
            else:
                try:
                    difficulty = int(difficulty.split("Difficulty rating: ")[1][:-1])
                except ValueError:
                    difficulty = int(
                        difficulty.split("Difficulty rating: ")[1].split(
                            " (Not yet finalised)"
                        )[0][:-1]
                    )
            question_number, prompt = prompt.split("\n", 1)
            question_number = int(question_number.split("Question ")[1])
            filename = os.path.join(dirname, "sources/solutions.txt")
            with open(filename, "r", encoding="utf-8") as file:
                solution = file.readlines()[question_number - 1].split(". ")[1].strip()
            questions.append((prompt, difficulty, solution))

    for index, question in enumerate(questions, 1):
        manager.add_to_db(
            prompt=question[0], difficulty=question[1], solution=question[2], id=index
        )


def main():
    """Run some basic functionality tests"""
    manager = ProblemManager()
    manager.create_table()
    print(manager.get_random_problem())
    print(manager.get_random_problem(min_difficulty=10))
    print(manager.get_random_problem(max_difficulty=50))
    print(manager.get_random_problem(min_difficulty=50, max_difficulty=70))


if __name__ == "__main__":
    main()
