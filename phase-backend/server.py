import os
import logging
import json
from bson import json_util
from datetime import datetime
from helpers import get_postgre_database

from quart import Quart, request, jsonify
from quart_cors import cors
from dotenv import load_dotenv

from storage.retriever import VectorRetriever
from storage.store_doc import store_doc
from recall_service import RecallService
# from agent import Agent

app = Quart(__name__)
app = cors(app, allow_origin="http://localhost:3000", allow_headers=["Content-Type"], allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_credentials=True)
# app = cors(app, allow_origin='http://localhost:3000', allow_credentials=True)
app.logger.setLevel(logging.DEBUG)

# start the vector retriever
load_dotenv()
database = os.environ["SUPABASE_DATABASE"]
collection = os.environ["SUPABASE_EMBEDDING_COLLECTION"]
connection_string = get_postgre_database(database=database)

vector_retriever = VectorRetriever(conn_string=connection_string, collection=collection)
recall_service = RecallService(db_connection=connection_string, collection=collection)
# agent = Agent(model="mistral-openorca:latest", vector_retriever=vector_retriever)
text = ""


@app.route('/embed_text', methods=['POST', 'OPTIONS'])
async def embed_text():
    print("In the embed text function")
    json_data = await request.form

    response = jsonify({})

    if request.method == 'OPTIONS':
        print("In the options method thing")
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        return response, 200

    # if not media:
    #     response.status_code = 100
    #     return response
    
    await store_doc(connection_string, json_data)
    print("Doc has been stored!")
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'

    return response

@app.route('/get_daily_summary', methods=['GET'])
def get_daily_summary():
    print("In the get summary function")

    date = datetime.now()

    summary = recall_service.get_daily_summary(date)
    # summary = "hey"
    print("Get daily summary server method succeeded")

    response = jsonify(summary)
    # response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    # response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, PUT, DELETE, OPTIONS"
    # response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, X-Auth-Token"
    response.status_code = 200
    
    return response



def parse_json(data):
    return json.loads(json_util.dumps(data))


@app.route('/get_daily_quiz', methods=['GET'])
def get_daily_quiz():
    print("In the get daily quiz function")
    user_id = 0
    summary, user_responses = recall_service.get_daily_quiz(user_id)
    print("Quiz has been created")
    result = {"quiz": summary, "user_responses": user_responses}

    response = jsonify(parse_json(result))
    print(response)
    response.status_code = 200
    
    return response


@app.route('/answer_question_from_quiz', methods=['POST'])
async def answer_question_from_quiz():
    print("In the get daily quiz function")
    data = await request.json
    print(data)
    data = data['quiz_contents']
    print(data)

    result = recall_service.answerQuestion(data['user_id'], data['quiz_id'], data['question'], data['answer'])
    print("Quiz has been answered")

    response = jsonify(parse_json(result))
    print(response)
    response.status_code = 200
    
    return response


@app.after_request
async def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response


@app.route('/')
async def main():
    return "Main package"

if __name__ == '__main__':
    app.run(debug=True)