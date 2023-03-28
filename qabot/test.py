from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.docstore.document import Document
from config import openai_api_key, WORKSPACE_PATH
import yaml
import os


loader = UnstructuredHTMLLoader("example_data/fake-content.html")
data = loader.load()


embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

def load_db():
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return db
def save_db():
    db = Chroma.from_documents(docs, embeddings, persist_directory=persist_directory)
    return db
