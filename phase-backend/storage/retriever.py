import psycopg2

from datetime import datetime, timedelta
from langchain.vectorstores.pgvector import PGVector
from langchain_community.embeddings import OllamaEmbeddings

# vector store backed retriever doc: https://python.langchain.com/docs/modules/data_connection/retrievers/vectorstore

class VectorRetriever:
    def __init__(self, conn_string: str, collection: str):
        self.conn_string = conn_string
        self.collection = collection
        self.embeddings = OllamaEmbeddings(model="llama2")

        self.store = PGVector(
            collection_name=self.collection,
            connection_string=self.conn_string,
            embedding_function=self.embeddings
        )
    
    def get_notes(self, link: str):
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        
        sql = "SELECT e.document FROM langchain_pg_embedding e JOIN langchain_pg_collection c ON e.uuid = c.uuid WHERE c.name = %s;"
        cur.execute(sql, (link,))
        docs = cur.fetchall()

        cur.close()
        conn.close()
        return docs
    

    def get_links(self, uuids: list):
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        
        placeholders = ', '.join(['%s'] * len(uuids))
        sql = f"SELECT name FROM langchain_pg_collection WHERE c.name IN ({placeholders});"
        cur.execute(sql, (uuids,))
        docs = cur.fetchall()

        cur.close()
        conn.close()
        return docs
    

    # TO DO, also add the time into the postgre database
    def get_relevant_links(self, datetime, k):
        conn = psycopg2.connect(self.conn_string)
        cursor = conn.cursor()

        column_name = "collection"

        one_day_ago = datetime.now() - timedelta(days=1)
        sql_query = f"SELECT {column_name} FROM your_table WHERE insertion_timestamp > %s"

        cursor.execute(sql_query, (one_day_ago,))

        values = cursor.fetchall()
        cursor.close()
        conn.close()
        return [value[0] for value in values]
    

    def get_docs(self, query: str, k=5, fetch_k=10):
        result = self.store.max_marginal_relevance_search(query, k=k, fetch_k=fetch_k)
        return result
    
    def get_context(self):
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        cur.execute("SELECT document FROM langchain_pg_embedding")
        docs = cur.fetchall()

        cur.close()
        conn.close()

        return docs