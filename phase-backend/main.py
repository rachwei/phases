import os
import asyncio
from typing import Optional

from helpers import get_postgre_database
from storage.retriever import VectorRetriever
from storage.store_doc import store_doc

# start the vector retriever
# connection_string = get_postgre_database("COLLECTION HERE")


# STORE DOC/FORM:
# to do: fix store_doc, make sure it works
# fix the document splitter + add the link? + the timestamp
# embed a link, note, and summary from the form

# implement createSummary, and test it out
# get similar links (test the retrieve k function)


# QUIZ FEATURE:
# look at the timestamps and choose the ones that you inputted today, then going back 7 days (etc)
# feed into a language model that has the right answer (RESEARCH HOW TO MAKE A QUIZ)
# 3 questions

# group the knowledge into different clusters
# visualize the different clusters
