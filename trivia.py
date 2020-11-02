import requests
import random
import signal
import sys
from datetime import datetime


def categories() -> list[tuple[int, str]]:
    """Returns a dictionary for list of categories"""

    category_url = "https://opentdb.com/api_category.php"
    response = requests.get(category_url).json()["trivia_categories"]
    print("\nWelcome Player", "\n")
    return (f"{cat_id-8}\t{name}" for cat_id, name in (category.values() for category in response))


def trivia_questions(category_id: int, /) -> list[dict[str, str, str, str, str]]:
    """Returns a list of dictionaries that contains the questions, difficulty, wrong answers, and answer"""

    params = {"amount": 10, "type": "multiple", "category": category_id}
    trivia_url = 'https://opentdb.com/api.php'
    response = requests.get(trivia_url, params=params)
    return response.json()["results"]


def selected_questions() -> list[dict[str, str]]:
    """Returns a list that contains 10 questions of varying difficulty"""

    print(*categories(), sep="\n")
    try:
        category = int(input("\nWhich category would you like to choose?\n"))+8

    except ValueError:
        return selected_questions()

    if not (category-8 > 0 and category-8 <= 24):
        return selected_questions()

    questions = random.sample(trivia_questions(category), k=10)
    question_sample = [{"question": question["question"],
                        "answer":question["correct_answer"],
                        "choices":"\n\t".join(sorted([question["correct_answer"], *question["incorrect_answers"]])),
                        "difficulty":question["difficulty"]}for question in questions]
    return question_sample


def signal_handler(sig, frame, /) -> None:
    """Handles keyboard interruption error"""

    print("\nexited game")
    sys.exit()


def update_score(file, score, callback):
    date = datetime.now()
    date_formatted = (f'{date:%m-%d-%y}')
    is_top_score = False
    with open(file, "a+") as f, open(file) as x:
        scores = x.read().splitlines()
        players = scores[3:]
        player_scores = (p.split()[1] for p in players)

        for top_score in player_scores:
            if score > int(top_score):
                is_top_score = True

                break

        if not scores or len(players) <= 10:
            print("\nYou have a top score!\n")
            name = input("Enter Initials\n")

            if not name:
                return callback(score)

            body = f"\n{name}{score:>15}{date_formatted:>20}"

            f.write(body)

        # elif len(players >= 10) and is_top_score:
        #     print("\nYou have a top score!\n")
        #     name = input("Enter Initials\n")
        #     if not name:
        #         return callback(score)

        #     header = f"{'Top Scores'.center(35)}\n{'-'*38}\nPlayer{'Score':>15}{'Date':>15}"
        #     body = f"{name}{score:>15}{date_formatted:>20}"
        #     new_list = sorted(players, key=lambda x: x.split()[0])
        #     print(new_list)
        #     new_list.pop()
        #     updated_list = new_list.append(body)
        #     print(updated_list)
        #     content = "\n".join([header, updated_list])
        #     x.writelines(content)
        # else:
        #     print("You didn't get a top score")


def top_score(score: int) -> str:
    """Displays top 10 player scores"""
    top_scores = "top_scores.txt"

    header = f"{'Top Scores'.center(35)}\n{'-'*38}\nPlayer{'Score':>15}{'Date':>15}"

    try:
        with open(top_scores, "x") as file:
            file.write(header)
        update_score(top_scores, score)
    except FileExistsError:
        update_score(top_scores, score, top_score)

    with open(top_scores) as t:
        print(t.read())


def main() -> int:
    """Runs the trivia game and returns the score"""

    questions = selected_questions()
    score = 0
    i = 0
    while (i < len(questions)):
        answer = input(
            f'\n{(item := questions[i])["question"]}\n\nChoices:\n\t{(item["choices"])}\n\nYour Answer: ')

        if answer.strip().lower().replace(" ", "") == item["answer"].lower().replace(" ", ""):
            if (difficulty := item["difficulty"]) == "easy":
                score += 10
            elif difficulty == "medium":
                score += 20
            else:
                score += 30

        print(f'\nYour score is {score}')
        i += 1
    return score


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, signal_handler)
        score = main()
        top_score(score)
    except Exception as e:
        print(e)

    else:
        print("\nGame over!")
