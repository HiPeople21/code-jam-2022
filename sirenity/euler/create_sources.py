import os

import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore


def create_prompts(file: str = "prompts.txt", *, solutions="sources/solutions.txt"):
    """Creates prompts file"""
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, solutions)
    with open(filename, "r", encoding="utf-8") as f:
        solutions = f.readlines()

    prompts = []
    for solution in solutions:
        try:
            number, solution = solution.split(". ")
            prompt = requests.get(f"https://projecteuler.net/minimal={number}").text
            soup = BeautifulSoup(
                requests.get(f"https://projecteuler.net/problem={number}").text
            )
            difficulty = soup.find("span", class_="tooltiptext_right").text.split(";")[  # type: ignore
                -1
            ]
            assert difficulty is not None
            prompt = prompt.replace(
                'href="project/resources',
                'href="https://projecteuler.net/project/resources',
            ).replace(
                'src="project/images', 'src="https://projecteuler.net/project/images'
            )
            prompts.append(f"Question {number}\n{prompt}\n----------\n{difficulty}")
        except ValueError:
            continue

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, f"sources/{file}")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n==========\n".join(prompts))


def create_solutions(file: str = "solutions.txt"):
    """Creates solutions file"""
    text = requests.get(
        "https://github.com/luckytoilet/projecteuler-solutions/blob/master/Solutions.md"
    ).text
    soup = BeautifulSoup(text)
    tbody = soup.find("pre", class_="notranslate").text  # type: ignore
    assert tbody is not None

    solutions = "\n".join(tbody.splitlines()[3:])
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, f"sources/{file}")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(solutions)


if __name__ == "__main__":
    pass
