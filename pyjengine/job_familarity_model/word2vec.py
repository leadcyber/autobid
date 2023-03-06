from gensim.models.keyedvectors import KeyedVectors
from .utils import to_understandable_skill_name

print("Loading Word2Vec model...")
word_vect = KeyedVectors.load_word2vec_format("./job_familarity_model/Model/SO_vectors_200.bin", binary=True)
print("Model loaded.")

def similarity_n1(skills, point):
    skills = [ to_understandable_skill_name(item) for item in skills ]
    return word_vect.n_similarity(skills, [point])

def similarity_nm(skills1, skills2):
    skills1 = [ to_understandable_skill_name(item) for item in skills1 ]
    skills2 = [ to_understandable_skill_name(item) for item in skills2 ]
    return word_vect.n_similarity(skills1, skills2)