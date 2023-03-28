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

introductions = []
try:
    with open(f'{WORKSPACE_PATH}/introduction.yaml', "r") as stream:
        introductions = yaml.safe_load(stream) or []
except: pass
print(introductions)
docs = [ Document(page_content=introduction, metadata={ "title": "intro" }) for introduction in introductions ]


skills = []
try:
    with open(f'{WORKSPACE_PATH}/skills.yaml', "r") as stream:
        skill_data = yaml.safe_load(stream)["skills"] or {}
        for key in skill_data:
            value = skill_data[key]
            skills.append(f'I have {value["exp"]} years of {key} experience.')
except: pass
docs.extend([ Document(page_content=skill, metadata={ "title": "skill" }) for skill in skills ])

docs.append(Document(page_content="I am available at any time to have an phone call for 5 minutes.", metadata={ "title": "availibility" }))
docs.append(Document(page_content="I am available for the 30 minutes video interview at any time.", metadata={ "title": "availibility" }))
docs.append(Document(page_content="I am available for the technical interview at any time.", metadata={ "title": "availibility" }))

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
