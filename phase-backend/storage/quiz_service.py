import os

from bson.objectid import ObjectId
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient


class QuizService:
    def __init__(self):
        load_dotenv()
        self.client = MongoClient(os.getenv('MONGODB_URL'))
        self.db = self.client[os.getenv('DB_NAME')]
        self.quiz_collection = self.db[os.getenv('QUIZ_COLLECTION_NAME')]
        self.user_responses = self.db[os.getenv('QUIZ_RESPONSE_COLLECTION_NAME')]

    def insert_quiz(self, user_id, quiz):
        """
        Inserts a new quiz into the database.
        
        Parameters:
        - quiz_data (dict): A dictionary containing the quiz data.
        """
        quiz_data = {
            "user_id": user_id,
            "questions": [
                {"question": q.question, "answers": q.answers, "correct_answer": q.correct_answer} for q in quiz.questions
            ],
            "date": quiz.date,
            "created_at": datetime.now()
        }

        result = self.quiz_collection.insert_one(quiz_data)
        return result


    def get_quiz_by_id(self, id):
        return self.quiz_collection.find_one({"_id": id})

    def get_quiz_from_day(self, date):
        return self.quiz_collection.find_one({"date": date})
    

    def update_user_response(self, user_id, quiz_id, question, answer):
        """
        Updates user's response for a particular question in the quiz.
        
        Parameters:
        - user_id (str): The ID of the user.
        - quiz_id (str): The ID of the quiz.
        - question (str): The question.
        - answer (str): The answer.
        
        Returns:
        - The object ID of the inserted or updated user response.
        """
        inserted_at = datetime.now()
        quiz_id = ObjectId(quiz_id['$oid'])

        print(quiz_id)
        correct_answer = self.quiz_collection.find_one(
            {'_id': quiz_id, 'questions.question': question},
            {'questions.$': 1}
        ).get('questions')[0].get('correct_answer')

        correct = answer == correct_answer
        print("The correct answer: ", correct_answer)
        print("Was correct? ", correct)
        exists = self.user_responses.find_one({'quiz_id': quiz_id})

        if exists:
            responses = exists.get('responses', [])
            print(responses)
            for resp in responses:
                if resp['question'] == question:
                    resp['correct'] = correct
                    self.user_responses.update_one({'user_id': user_id, 'quiz_id': quiz_id, 'responses.question': question}, {'$set': {'responses.$.correct': correct}})
                    return exists['_id']

            responses.append({'question': question, 'correct': correct})
            result = self.user_responses.update_one({'user_id': user_id, 'quiz_id': quiz_id}, {'$set': {'responses': responses, 'inserted_at': inserted_at}}, upsert=True)
            return exists['_id']
        else:
            result = self.user_responses.insert_one({'user_id': user_id, 'quiz_id': quiz_id, 'responses': [{'question': question, 'correct': correct}], 'inserted_at': inserted_at})
            return result.inserted_id


    def get_user_responses(self, user_id, quiz_id):
        return self.user_responses.find_one({'quiz_id': quiz_id, 'user_id': user_id})
    
    
    def find_quiz_by_id(self, quiz_id):
        """
        Finds a quiz by its ID.
        
        Parameters:
        - quiz_id (str): The ID of the quiz to find.
        
        Returns:
        - A dictionary representing the quiz if found, otherwise None.
        """
        quiz = self.quiz_collection.find_one({'_id': quiz_id})
        return quiz


if __name__ == "__main__":
    print("yey")

# # Find the quiz by its ID
# found_quiz = quiz_service.find_quiz_by_id(quiz_id)
# print("Found quiz:", found_quiz)
# quiz_id = "663d27ec309a8cac5a52576e"

# Example usage of update_user_response method
# user_id = "example_user_id"
# question_id = 1
# correct = True

# # First response to the question
# inserted_id = quiz_service.update_user_response(user_id, quiz_id, question_id, correct)
# print("Inserted user response ID:", inserted_id)

# # Second response to the same question (updating the previous response)
# correct = False
# inserted_id = quiz_service.update_user_response(user_id, quiz_id, question_id, correct)
# print("Updated user response ID:", inserted_id)

# # Third response to the question (updating the previous response)
# correct = True
# inserted_id = quiz_service.update_user_response(user_id, quiz_id, 2, correct)
# print("Updated user response ID:", inserted_id)