from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import VectorDBQA
from langchain.llms import OpenAI
from langchain.docstore.document import Document
from engine import vectordb
from config import openai_api_key
from langchain.chains.question_answering import load_qa_chain

db = vectordb.load_db()
openai = OpenAI(temperature=0, openai_api_key=openai_api_key)
chain = load_qa_chain(openai, chain_type="stuff", verbose=False)

while True:
    query = input()
    docs = db.similarity_search(query)
    print([ item.page_content for item in docs ])
    res = chain.run(input_documents=docs, question=query)
    print(res)
# db = Chroma.from_documents(qa_docs, embeddings, persist_directory=persist_directory)

# similarities = db.similarity_search("where do you live?")
# print([ item.page_content for item in similarities ])

# qa = VectorDBQA.from_chain_type(llm=ChatOpenAI(), chain_type="stuff", vectorstore=db, k=1)

# question = "What is the document about"
# answer = qa.run(question)
# print(answer)
