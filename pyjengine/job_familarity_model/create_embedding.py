from langchain.embeddings import OpenAIEmbeddings
from skill.utils import normalize_skill_name
from config import OPENAI_API_KEY, WORKSPACE_PATH
import yaml

from gensim.models.keyedvectors import KeyedVectors

print("Reading skill yaml data ...")
skill_names = []
skills = []
try:
    with open(f'{WORKSPACE_PATH}/skills.yaml', "r") as stream:
        skill_data = yaml.safe_load(stream)["skills"] or {}
        for key in skill_data:
            value = skill_data[key]
            if "embedding" in value:
                skills.append(value["embedding"])
                skill_names.append(normalize_skill_name(key))
except: pass

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

print("Calculating vectors using OpenAI ...")
vectors = embeddings.embed_documents(skills)

if len(vectors) == 0:
    exit()

print("Creating KeyedVectors ...")
vector_dim = len(vectors[0])
print("Embedding dim: ", vector_dim)
word_vect = KeyedVectors(vector_dim)
word_vect.add_vectors(skill_names, vectors)
word_vect.save_word2vec_format('./job_familarity_model/Model/openai_powered_embedding.bin', binary=True)
