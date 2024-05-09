import sys

# sys.path.append("..")
from ollama_client import generate

DEFAULT_MODEL = "mistral-openorca:latest"


def summarize_prompt(
    link: str,
    notes: str,
    model=DEFAULT_MODEL,
):
    SYS_PROMPT = (
        "You are a . Your task is to choose one question "
        "from a given list of 'unanswered questions' (delimited by ```). "
        "You are provided with a 'goal question' and a numbered list of 'unanswered questions' as inputs. "
        "Think about which question out of the given list of questions can help you answer the 'goal question'. "
        "Don't choose a question that doesn't seem to relate to the 'goal question'."
        "Choose one and only one question from the list of 'unanswered questions'.\n"
        "Respond with the choosen question as it is, ditto without any edits."
        " Remember the format of the output should look like:\n"
        " question_id. question"
    )

    prompt = (
        f"Link: ``` {link} ```.\n\n"
        f"Notes:  ``` {notes} ```\n\n"
        "Your response:"
    )

    response, _ = generate(model=model, system=SYS_PROMPT, prompt=prompt)
    return response


def get_quiz(
    notes: str,
    model=DEFAULT_MODEL
):
    SYS_PROMPT = (
        " You are a teacher that wants to test the comprehension of your students on a piece of text."
        " You will be provided with some 'notes' on a subject."
        " Your task is to create a list of multiple choice questions from the information given in the 'notes'."
        " For each question, you will also come up with 4 possible multiple choice answers with only one correct answer. "
        # " You can use the following chain of thoughts:\n"
        # " \tThought 1: Concepts. What are the entities like subject, predicate, etc. mentioned in the question?\n"
        # " \tThought 2: Context. What additional context may help you know more about these entities to answer the question?\n"
        # " Do not use any prior knowledge. If it is not possible to make a hypothesis, return the original question."
        " ['First Question', 'Second Question', ...]"
        " Format your answer as the following: \n"
        " Questions: ['First Question', 'Second Question', ...] \n"
        " Context: \n"
    )

    prompt = f" Notes: ``` {notes} ``` \n Your response:"

    response, _ = generate(model=model, system=SYS_PROMPT, prompt=prompt)
    return response