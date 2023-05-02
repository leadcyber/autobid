from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.docstore.document import Document
from config import openai_api_key, WORKSPACE_PATH
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain


loader = UnstructuredHTMLLoader("example_data/jd.html")
docs = loader.load()
print(docs)

openai = OpenAI(temperature=0, openai_api_key=openai_api_key)
chain = load_qa_chain(openai, chain_type="map_reduce", verbose=False)
print("Input your query.")
while True:
    query = input()
    res = chain.run(input_documents=docs, question=query)
    print(res)