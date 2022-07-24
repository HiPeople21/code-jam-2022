import csv
import pathlib
import re
from typing import TextIO

import requests
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).parent
SOLUTION_REGEX = re.compile(
    r"""
    (?P<id>\d+)\. # Matches the problem id
    \ ? # Optional space
    (?P<solution>\d+|) # Matches the solution
    """,
    re.VERBOSE,
)

DIFFICULTY_RATING_REGEX = re.compile(
    r"""
    Difficulty\ rating:\  # All difficulty ratings begin with 'Difficulty rating: '
    (?P<rating>\d+)% # Parse the difficulty rating
    (\ \(Not\ yet\ finalised\))? # Some difficulty ratings are not yet finalised
    """,
    re.VERBOSE,
)


def download_prompts(outfile, solutions):
    """Creates file containing Project Euler prompts"""
    writer = csv.DictWriter(outfile, ["id", "prompt", "solution", "difficulty"])
    writer.writeheader()
    for problem_id, solution in solutions.items():
        print(f"Downloading prompt for Project Euler problem {problem_id}")
        prompt = (
            requests.get(f"https://projecteuler.net/minimal={problem_id}")
            .text.replace(
                "project/resources",
                "https://projecteuler.net/project/resources",
            )
            .replace("project/images", "https://projecteuler.net/project/images")
        )

        soup = BeautifulSoup(
            requests.get(f"https://projecteuler.net/problem={problem_id}").text,
            features="lxml",
        )

        tooltip_text = soup.find("span", class_="tooltiptext_right").text

        if tooltip_text is None:
            raise ValueError(f"Error while downloading prompt for problem {problem_id}")

        # The difficulty string is the last string in a list of semi-colon separated strings
        difficulty_text = tooltip_text.split(";")[-1]
        result = re.fullmatch(DIFFICULTY_RATING_REGEX, difficulty_text)
        if result is None:
            raise ValueError(
                f"Unable to parse difficulty rating for problem {problem_id} (got '{difficulty_text}')"
            )

        writer.writerow(
            {
                "id": problem_id,
                "prompt": prompt,
                "solution": solution,
                "difficulty": result.group("rating"),
            }
        )


def download_solutions(maximum=None):
    """Creates solutions file"""
    text = requests.get(
        "https://raw.githubusercontent.com/luckytoilet/projecteuler-solutions/master/Solutions.md"
    ).text

    solutions = {}

    number = 0
    for line in text.splitlines():
        # If we've received enough, stop loading solutions
        if maximum and number == maximum:
            break

        result = re.fullmatch(SOLUTION_REGEX, line)

        # Ignore lines that do not match
        if result is None:
            continue

        problem_id = result.group("id")
        solution = result.group("solution")

        # Skip problems with no solutions given
        if solution:
            solutions[problem_id] = solution
            number += 1

    return solutions


def setup_project_euler(outfile: TextIO):
    """Downloads the necessary content for Project Euler problems"""
    solutions = download_solutions(maximum=10)
    print("Downloaded Project Euler solutions")

    download_prompts(outfile, solutions)
    print("Downloaded Project Euler prompts")


def main():
    """Stores Project Euler content in the euler.csv file"""
    with open(ROOT / "euler.csv", "w") as file:
        setup_project_euler(file)

    print("Done!")


if __name__ == "__main__":
    main()
