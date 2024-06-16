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


def summarize_notes(
    notes: str,
    model=DEFAULT_MODEL,
):  
    print("Summarizing notes from notes", notes)
    SYS_PROMPT = (
        " You are a researcher that wants summarize your findings ."
        " You will be provided with some 'notes' from various sources ."
        " Your task is to summarize these notes in a concise manner and pick out several themes."
        " If you're unable to create a well thought out summary, then just return the original notes."
        # " You can use the following chain of thoughts:\n"
        # " \tThought 1: Concepts. What are the entities like subject, predicate, etc. mentioned in the question?\n"
        # " \tThought 2: Context. What additional context may help you know more about these entities to answer the question?\n"
        # " Do not use any prior knowledge. If it is not possible to make a hypothesis, return the original question."
    )

    prompt = (
        f"Notes:  ``` {notes} ```\n\n"
        "Your response:"
    )

    response, _ = generate(model=model, system=SYS_PROMPT, prompt=prompt)
    return response


def get_quiz(
    notes: str,
    model=DEFAULT_MODEL
):
    #'["Q1", "Q2", "Q3"]; [["A1", "A2", "A3", "A4"]. ["B1", "B2", "B3"]. ["C1", "C2", "C3", "C4"]]'
    SYS_PROMPT = (
        " You are a teacher that wants to test the comprehension of your students on a piece of text."
        " You will be provided with some 'notes' on a subject."
        " Your task is to create a list of multiple choice questions from the information given in the 'notes'."
        " For each question, you will also come up with 4 possible multiple choice answers with only one correct answer. "
        # " You can use the following chain of thoughts:\n"
        # " \tThought 1: Concepts. What are the entities like subject, predicate, etc. mentioned in the question?\n"
        # " \tThought 2: Context. What additional context may help you know more about these entities to answer the question?\n"
        # " Do not use any prior knowledge. If it is not possible to make a hypothesis, return the original question."
        " Each question number X, has four answers A_X, B_X, C_X, D_X and one of the answers is the correct one."
        " Format your answer as the following: \n"
        " ['Q_A', 'Q_B', 'Q_C']; [['A1', 'A2', 'A3', 'A4']. ['B1', 'B2', 'B3', 'B4']. ['C1', 'C2', 'C3', 'C4']]\n"
        " Context: \n"
    )

    prompt = f" Notes: ``` {notes} ``` \n Your response:"

    response, _ = generate(model=model, system=SYS_PROMPT, prompt=prompt)
    return response