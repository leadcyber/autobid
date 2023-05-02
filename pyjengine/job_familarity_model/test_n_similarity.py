from skill.utils import normalize_skill_name
from .word2vec import word_vect

while True:
    temp = input()
    skills1 = [ normalize_skill_name(item) for item in temp.split(" ") ]
    temp = input()
    skills2 = [ normalize_skill_name(item) for item in temp.split(" ") ]
    print(word_vect.n_similarity(skills1, skills2))

# while True:
#     temp = input()
#     skills1 = [ to_embedding_skill_name(item) for item in temp.split(" ") ]
#     temp = input()
#     skills2 = [ to_embedding_skill_name(item) for item in temp.split(" ") ]
#     print(word_vect.n_similarity(skills1, skills2))

# while True:
#     temp = input()
#     skills = [ to_embedding_skill_name(item) for item in temp.split(" ") ]
#     print(word_vect.rank_by_centrality(skills))


# while True:
#     skill1 = to_embedding_skill_name(input())
#     while skill1 not in word_vect:
#         print("Not found in embedding")
#         skill1 = to_embedding_skill_name(input())
#         continue

#     skill2 = to_embedding_skill_name(input())
#     while skill2 not in word_vect:
#         print("Not found in embedding")
#         skill2 = to_embedding_skill_name(input())
#         continue

#     print(word_vect.distances(skill1, [skill2]))