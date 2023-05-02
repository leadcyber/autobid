from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import VectorDBQA
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from config import openai_api_key, WORKSPACE_PATH
import yaml
import os


persist_directory = 'qdb'

docs = []

skills = []
try:
    with open(f'{WORKSPACE_PATH}/skills.yaml', "r") as stream:
        skill_data = yaml.safe_load(stream)["skills"] or {}
        for key in skill_data:
            value = skill_data[key]
            if "embedding" in value:
                skills.append(value["embedding"])
except: pass
docs.extend([ Document(page_content=skill, metadata={ "title": "skill" }) for skill in skills ])

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

def load_db():
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return db
def save_db():
    db = Chroma.from_documents(docs, embeddings, persist_directory=persist_directory)
    return db

# similarities = db.similarity_search("where do you live?")
# print([ item.page_content for item in similarities ])

# qa = VectorDBQA.from_chain_type(llm=ChatOpenAI(), chain_type="stuff", vectorstore=db, k=1)

# question = "What is the document about"
# answer = qa.run(question)
# print(answer)
