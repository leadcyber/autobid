from gensim.models.keyedvectors import KeyedVectors
from skill.utils import normalize_skill_name

print("Loading Word2Vec model...")
word_vect = KeyedVectors.load_word2vec_format("./job_familarity_model/Model/openai_powered_embedding.bin", binary=True)
# word_vect = KeyedVectors.load_word2vec_format("./job_familarity_model/Model/SO_vectors_200.bin", binary=True)
# word_vect = KeyedVectors.load_word2vec_format("./job_familarity_model/Model/se_wiki_w2v_SKIPGRAM.bin", binary=True)
print("Model loaded.")

def similarity_n1(skills, point):
    skills = [ normalize_skill_name(item) for item in skills ]
    return word_vect.n_similarity(skills, [point])

def similarity_nm(skills1, skills2):
    if len(skills1) == 0 or len(skills2) == 0:
        return 0
    skills1 = [ normalize_skill_name(item) for item in skills1 ]
    skills2 = [ normalize_skill_name(item) for item in skills2 ]
    return word_vect.n_similarity(skills1, skills2)