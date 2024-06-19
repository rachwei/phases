import asyncio
import psycopg2
from datetime import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.vectorstores.pgvector import PGVector
from langchain_community.embeddings import OllamaEmbeddings
from helpers import get_postgre_database


async def store_doc(db_connection: str, json_data: dict):
    embeddings = OllamaEmbeddings(model="llama2")
    print("Store doc connection string: %s", db_connection)

    text_splitter = CharacterTextSplitter()
    link = json_data["link"]
    notes = json_data["notes"]

    texts = text_splitter.split_text(notes)
    documents = [Document(page_content=t) for t in texts]
    print(documents)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1100,
        chunk_overlap=150,
        length_function=len,
        is_separator_regex=False,
    )

    pages = splitter.split_documents(documents)
    print("Number of chunks = ", len(pages))

    inserted_vector = PGVector.from_documents(
        embedding=embeddings,
        documents=pages,
        collection_name=link,
        connection_string=db_connection,
        pre_delete_collection=True,
    )

    # insert time to the inserted vector - make this more efficient later (TEST LATER)
    try:
        conn = psycopg2.connect(db_connection)
        sql = "UPDATE langchain_pg_collection SET newest_entry = %s WHERE name = %s"
        data = (datetime.now(), link)

        cur = conn.cursor()
        cur.execute(sql, data)
        cur.close()
        conn.commit()

        print("Update successful")
    except Exception as e:
        print("Error:", e)
        conn.rollback()
    finally:
        conn.close()

    print("Added pages!")



if __name__ == '__main__':
    connection_string = get_postgre_database("phase")
    collection = "embeddings"
    asyncio.run(store_doc(connection_string, collection, "ok2 this is a asldkfjasldkfjaslkdfjalskdfjalskdfjalskfjasdldkfjasklfjlkasdfjklasjdflkajsdfklasdjfklasjdfklasjfklasjdfklasjdfklasfjklasdfjklasfjkladsjfkladsjfklasjfklasjfklasjdfklasjdfklasjfklasjfklasjdfklasjdflkasjdfklajsfklasjdflkajslfkajskldfjalksdfjlaksdfjklasdfjlksdadjflkasfjlkasdfjklasfjksaldfjlkasdjfklsadfjdasklfjklasfjklasdfjkasldfjadklsfjdkaslfjksaldfjlkasfjlasdkfjsadlkfjksaldfjlksadfjklsadfjlksdfjlsadkfj"))



# @app.route('/embed_text', methods=['post'])
# async def embed_text():
#     print("In the embed text function")
#     data = await request.files
#     media = data.getlist('files')
#     print(media)
    
#     response = jsonify({})
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     request.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, PUT, DELETE, OPTIONS"
#     request.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, X-Auth-Token"

#     if not media:
#         response.status_code = 100
#         return response
    
#     text = getText(media)
#     print("Text output: ", text)
#     await store_doc(connection_string, collection, text)
#     print("Doc has been stored!")
#     response.status_code = 200

#     return response
    

    # conn = psycopg2.connect(db_connection)
    # cur = conn.cursor()
    # table_create_command = f"""
    #     DELETE FROM langchain_pg_embedding;
    # """
    # cur.execute(table_create_command)
    # # cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    # cur.close()
    # conn.commit()