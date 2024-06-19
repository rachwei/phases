import ast
import os
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Optional

from prompts import summarize_prompt, get_quiz, summarize_notes
from helpers import get_postgre_database

from storage.quiz_service import QuizService
from storage.user_service import UserService
from storage.retriever import VectorRetriever
from storage.store_doc import store_doc


# what if you could add tags, like obsidian


class Question:
    question: str
    answers: list[str]
    correct_answer: str

    def __init__(self, question, answers, correct_answer):
        self.question = question
        self.answers = answers
        self.correct_answer = correct_answer


class Quiz:
    questions : List[Question] = []
    date : datetime

    def __init__(self, questions, date):
        self.questions = questions
        self.date = date
 
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


    def get_quiz_content(self, notes):
        result = get_quiz(notes) #'["Q1", "Q2", "Q3"]; [["A1", "A2", "A3", "A4"]. ["B1", "B2", "B3"]. ["C1", "C2", "C3", "C4"]]'
        print("Result from get quiz prompt:", result)
        # "['Who is my favorite singer?', 'You', 'Me', 'Mom', 'Dad'].['Who is my favorite binger?', 'Me', 'You', 'Mom', 'Dad']"

        # items = [item.strip() for item in result.split('.')]
        # questions = ast.literal_eval(items[0])
        # answers = items[1][1:-1]
        # answers = [ans.strip() for ans in answers.split('.')]
        # answers = [ast.literal_eval(ans) for ans in answers]
        items = [item.strip() for item in result.split('.')]
        questions = []
        questions = [
            Question(
                question=(eval := ast.literal_eval(item))[0],
                answers=eval[1:],
                correct_answer=eval[1]
            )
            for item in items
        ]
        
        return questions
    

    def get_relevant_links(self):
        now = datetime.now()
        relevant_links = self.retriever.get_relevant_links(now)

        # print("Relevant links: ", relevant_links)
        # notes = "\n----\n".join(
        #     [f"{doc.page_content}" for doc in relevant_links]
        # )
        return relevant_links
    
    def get_daily_quiz(self, user_id):
        current_date = datetime.now().date().isoformat()
        daily_quiz = self.quiz_service.get_quiz_from_day(current_date)

        if daily_quiz is None:
            return self.create_quiz(current_date)
        
        print("Daily quiz: ", daily_quiz)
        user_responses = self.quiz_service.get_user_responses(user_id, daily_quiz['_id'])

        return daily_quiz, user_responses

    def create_quiz(self, date):
        relevant_links = self.get_relevant_links()

        notes = ' '.join([self.get_notes(link) for link in relevant_links])
        question_objs = self.get_quiz_content(notes) # returns [Q1, Q2, Q3], [[A1, A1, A1, A1], [A2, A2, A2]]...
        print("Creating quiz question objs:", question_objs)

        quiz = Quiz(question_objs, date)
        inserted_quiz = self.quiz_service.insert_quiz(0, quiz)
        print("Inserted quiz:", inserted_quiz)
        return inserted_quiz
    
    def answerQuestion(self, user_id: dict, quiz_id: str, question: str, answer: str):
        id = self.quiz_service.update_user_response(user_id, quiz_id, question, answer)
        return id


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
    load_dotenv()
    database = os.environ["SUPABASE_DATABASE"]
    collection = os.environ["SUPABASE_EMBEDDING_COLLECTION"]
    connection_string = get_postgre_database(database=database)

    recall_service = RecallService(connection_string, collection)
    result = recall_service.get_daily_quiz(0)
    # result = '["Q1", "Q2", "Q3"]; [["A1", "A2", "A3", "A4"]. ["B1", "B2", "B3"]. ["C1", "C2", "C3", "C4"]]'
    # items = [item.strip() for item in result.split(';')]

    # questions = ast.literal_eval(items[0])
    # print(questions)

    # answers = items[1][1:-1]
    # answers = [ans.strip() for ans in answers.split('.')]
    # answers = [ast.literal_eval(ans) for ans in answers]
    # print(answers)

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