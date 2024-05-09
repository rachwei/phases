from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from prompts import summarize_prompt
from prompts import get_quiz
from storage.retriever import VectorRetriever
from storage.store_doc import store_doc


# what if you could add tags, like obsidian

@dataclass
class Question:
    question: str
    answers: dict

    def __init__(self, question, answers):
        self.question = question
        self.answers = answers

    def get_correct_answer(self):
        return [key for key, value in self.answers.items() if value]


@dataclass
class Quiz:
    questions : List[Question] = []
    date : datetime

    def __init__(self, id):
        self.date = datetime.now()
 
    def make_quiz(self, questions, answers):
        # cast questions/answers into the correct type

        for question in questions:
            question_obj = self.make_question(question)
            self.questions.append(question_obj)


    def make_question(self, question: str, answers: dict):
        return Question(question=question, answers=answers)



class RecallService:
    # store this in another database later!
    knowledge_points = 0

    def __init__(self, db_connection, collection):
        self.retriever = VectorRetriever()
        self.db_connection = db_connection
        self.collection = collection
    

    def getSimilarLinks(self, link: str):
        relevant_docs = VectorRetriever.get_notes(link)
    
        print("Relevant docs: ", relevant_docs)
        notes = "\n----\n".join(
            [f"{doc.page_content}" for doc in relevant_docs]
        )

        related_docs = VectorRetriever.get_docs(notes, k=3)
        related_uuids = list(set([{doc.uuid} for doc in related_docs]))

        related_links = VectorRetriever.get_links(related_uuids)
        return related_links


    def createSummary(self, link: str):
        notes = self.getNotes(link)
        response = summarize_prompt(link, notes)
        return response


    def createQuiz(self, link: str):
        notes = self.getNotes(link)
        questions, answers = get_quiz(link, notes) # returns [Q1, Q2, Q3], [[A1, A1, A1, A1], [A2, A2, A2]]...
        quiz = Quiz(questions, answers)

        # insert it into the database

        return quiz
    
    def answerQuestion(self, user_id: int, quiz_id: int, question_id: int, is_correct: bool):
        # insert into the user response database
        # at end of quiz, see how many responded correctly
        


    def getNotes(self, link):
        relevant_docs = VectorRetriever.get_notes(link)
        print("Relevant docs: ", relevant_docs)
        notes = "\n----\n".join(
            [f"{doc.page_content}" for doc in relevant_docs]
        )
        return notes

    async def embed_text(self, link: str, notes: str, summary: Optional[str]):
        if not summary:
            summary = self.createSummary(link, notes)
            await store_doc(self.db_connection, self.collection, link, notes, summary)


if __name__ == '__main__':
    recall_service = RecallService()