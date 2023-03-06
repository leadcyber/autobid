from skill.utils import get_skill_list
from .utils import to_understandable_skill_name
from .word2vec import word_vect

print("")
print("---------------------------------")
skills = get_skill_list()
unknown_skill_names = []
for index, full_name in enumerate(skills):
    skill_name = to_understandable_skill_name(full_name)
    if skill_name not in word_vect:
        unknown_skill_names.append(skill_name)
if len(unknown_skill_names) > 0:
    print("\n".join(unknown_skill_names))
    while True:
        word = input()
        word = to_understandable_skill_name(word)
        if word not in word_vect:
            print("No")
        else:
            print("Yes")
else:
    print("All passed!")
print("---------------------------------")
print("")
