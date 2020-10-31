import requests
import random
import signal
import sys


def categories() -> list[tuple[int, str]]:
    """Returns a dictionary for list of categories"""

    category_url = "https://opentdb.com/api_category.php"
    response = requests.get(category_url).json()["trivia_categories"]
    print("\nWelcome Player", "\n")
    return (f"{cat_id-8}\t{name}" for cat_id, name in (category.values() for category in response))


def trivia_questions(category_id: int, /) -> None:

    params = {"amount": 10, "type": "multiple", "category": category_id}
    trivia_url = 'https://opentdb.com/api.php'
    response = requests.get(trivia_url, params=params)
    return response.json()["results"]


def selected_questions() -> list[dict[str, str]]:
    print(*categories(), sep="\n")
    category = int(input("\nWhich category would you like to choose?\n"))+8

    if not (category-8 > 0 and category-8 <= 24):
        return selected_questions()

    questions = random.sample(trivia_questions(category), k=10)
    question_sample = [{"question": question["question"],
                        "answer":question["correct_answer"],
                        "choices":"\n\t".join(sorted([question["correct_answer"], *question["incorrect_answers"]])),
                        "difficulty":question["difficulty"]}for question in questions]
    return question_sample


def signal_handler(sig, frame, /) -> None:
    print("\nexited game")
    sys.exit()


def main():
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


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, signal_handler)
        main()
    except Exception as e:
        print(e)

    else:
        print("Game over!")
