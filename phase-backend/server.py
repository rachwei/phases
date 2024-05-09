import os
import asyncio
import logging
from helpers import get_postgre_database

from quart import Quart, render_template, websocket, current_app, request, jsonify
from quart_cors import cors
from dotenv import load_dotenv

from storage.retriever import VectorRetriever
from storage.store_doc import store_doc
# from agent import Agent

app = Quart(__name__)
app = cors(app)
app.logger.setLevel(logging.DEBUG)

# start the vector retriever
load_dotenv()
database = os.environ["SUPABASE_DATABASE"]
collection = os.environ["SUPABASE_EMBEDDING_COLLECTION"]
connection_string = get_postgre_database(database=database)

vector_retriever = VectorRetriever(conn_string=connection_string, collection=collection)
# agent = Agent(model="mistral-openorca:latest", vector_retriever=vector_retriever)
text = ""


@app.route('/embed_text', methods=['post'])
async def embed_text():
    print("In the embed text function")
    json_data = await request.form

    response = jsonify({})
    response.headers['Access-Control-Allow-Origin'] = '*'
    request.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, PUT, DELETE, OPTIONS"
    request.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, X-Auth-Token"

    # if not media:
    #     response.status_code = 100
    #     return response
    
    await store_doc(connection_string, json_data)
    print("Doc has been stored!")
    response.status_code = 200

    return response


@app.route('/')
async def main():
    return "Main package"

if __name__ == '__main__':
    app.run(debug=True)