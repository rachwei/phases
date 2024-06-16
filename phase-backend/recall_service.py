import ast

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from prompts import summarize_prompt, get_quiz, summarize_notes

from storage.quiz_service import QuizService
from storage.user_service import UserService
from storage.retriever import VectorRetriever
from storage.store_doc import store_doc


# what if you could add tags, like obsidian


class Question:
    question: str
    answers: dict

    def __init__(self, question, answers, correct_answer):
        self.question = question
        self.answers = answers
        self.correct_answer = correct_answer


class Quiz:
    questions : List[Question] = []
    date : datetime

    def __init__(self, link, questions):
        self.date = datetime.now()
        self.link = link
        self.questions = questions
 
    def populate_quiz(self, questions, answers, correct_answers):
        for i in range(len(questions)):
            question_obj = self.make_question(questions[i], answers[i], correct_answers[i])
            self.questions.append(question_obj)

    def make_question(self, question: str, answers, correct_answer):
        return Question(question=question, answers=answers, correct_answer=correct_answer)



class RecallService:
    # store this in another database later!
    knowledge_points = 0

    def __init__(self, db_connection, collection):
        self.retriever = VectorRetriever(db_connection, collection)
        self.db_connection = db_connection
        self.collection = collection

        self.user_service = UserService()
        self.quiz_service = QuizService()
    

    def getSimilarLinks(self, link: str):
        relevant_docs = self.retriever.get_notes(link)
    
        print("Relevant docs: ", relevant_docs)
        notes = "\n----\n".join(
            [f"{doc.page_content}" for doc in relevant_docs]
        )

        related_docs = self.retriever.get_docs(notes, k=3)
        related_uuids = list(set([{doc.uuid} for doc in related_docs]))

        related_links = self.retriever.get_links(related_uuids)
        return related_links


    def create_summary(self, link: str):
        notes = self.get_notes(link)
        response = summarize_prompt(link, notes)
        return response
    

    def get_daily_summary(self, date: datetime):
        # get notes from today
        # feed into prompt
        print("In the get daily summary function")
        notes = self.get_notes_from_relevant_links()
        print(notes)

        if not len(notes):
            return "You have no saved notes today!"
        
        response = summarize_notes(notes)
        return response
    
    
    def get_notes_from_relevant_links(self):
        relevant_links = self.get_relevant_links()
        notes = ' '.join([self.get_notes(link) for link in relevant_links])
        print("Output from get notes from relevant notes: ", notes)
        return notes


    def get_quiz_content(self, link, notes):
        result = get_quiz(link, notes) #'["Q1", "Q2", "Q3"]; [["A1", "A2", "A3", "A4"]. ["B1", "B2", "B3"]. ["C1", "C2", "C3", "C4"]]'
        items = [item.strip() for item in result.split(';')]

        questions = ast.literal_eval(items[0])
        answers = items[1][1:-1]
        answers = [ans.strip() for ans in answers.split('.')]
        answers = [ast.literal_eval(ans) for ans in answers]
        
        return questions, answers
    

    def get_relevant_links(self):
        now = datetime.now()
        print(type(now))
        relevant_links = self.retriever.get_relevant_links(now)

        # print("Relevant links: ", relevant_links)
        # notes = "\n----\n".join(
        #     [f"{doc.page_content}" for doc in relevant_links]
        # )
        return relevant_links

    def create_quiz(self, ):
        # get all information, not just from a single link
        relevant_links = self.get_relevant_links()

        notes = [self.get_notes(link) for link in relevant_links].join()
        questions, answers = self.get_quiz_content(notes) # returns [Q1, Q2, Q3], [[A1, A1, A1, A1], [A2, A2, A2]]...
        question_objs = [Question(questions[i], answers[i], answers[i][0]) for i in range(len(questions))]

        quiz = Quiz(question_objs)
        id = self.quiz_service.insert_quiz(quiz)

        return id
    
    def answerQuestion(self, user_id: int, quiz_id: int, question_id: int, is_correct: bool):
        # insert into the user response database
        # at end of quiz, see how many responded correctly
        id = self.quiz_service.update_user_response(self, user_id, quiz_id, question_id, is_correct)
        return id is not None


    def get_notes(self, link):
        print("Getting notes for link", link)
        notes = self.retriever.get_notes(link)
        total_notes = "\n----\n".join(
            [f"{doc[0]}" for doc in notes]
        )
        print("Notes: ", total_notes)
        return total_notes

    async def embed_text(self, link: str, notes: str, summary: Optional[str]):
        if not summary:
            summary = self.create_summaryy(link, notes)
            await store_doc(self.db_connection, self.collection, link, notes, summary)


if __name__ == '__main__':
    # db_connection = os.getenv('QUIZ_COLLECTION_NAME')
    # collection = os.getenv('QUIZ_COLLECTION_NAME')

    # recall_service = RecallService(db_connection, collection)
    # recall_service.
    result = '["Q1", "Q2", "Q3"]; [["A1", "A2", "A3", "A4"]. ["B1", "B2", "B3"]. ["C1", "C2", "C3", "C4"]]'
    items = [item.strip() for item in result.split(';')]

    questions = ast.literal_eval(items[0])
    print(questions)

    answers = items[1][1:-1]
    answers = [ans.strip() for ans in answers.split('.')]
    answers = [ast.literal_eval(ans) for ans in answers]
    print(answers)

    # first_list = parsed_items[0]
    # second_list = parsed_items[1:]

    # print("First list:", first_list)
    # print("Second list:", second_list)



    # quiz_service = QuizService()
    
    # questions = [Question("What is 2 + 2?", ["1", "2", "3", "4"], "4"), 
    #              Question("What is the capital of France?", ["London", "Paris", "Madrid", "Washington", "Paris"], "Paris")]
    # quiz = Quiz(questions)

    # quiz_id = quiz_service.insert_quiz("hell", quiz)
    # print("Inserted quiz with ID:", quiz_id)

    # found_quiz = quiz_service.find_quiz_by_id(quiz_id)
    # print("Found quiz:", found_quiz)