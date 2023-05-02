from skill.utils import normalize_skill_name
from .word2vec import word_vect

while True:
    temp = input()
    skills1 = [ normalize_skill_name(item) for item in temp.split(" ") ]
    temp = input()
    skills2 = [ normalize_skill_name(item) for item in temp.split(" ") ]
    if '' in skills1:
        skills1.remove('')
    if '' in skills2:
        skills2.remove('')
    try:
        print(word_vect.most_similar(positive=skills1, negative=skills2))
    except:
        print("Vector not found.")
