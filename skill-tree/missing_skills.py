from urllib import request, parse
import json

SERVICE_URL = "http://localhost:7000"

def get_skills():
    req = request.Request(f'{SERVICE_URL}/skill/list', method="GET") # this will make the method "POST"
    response = request.urlopen(req)
    return json.loads(response.read())

def get_additional_sentences():
    req = request.Request(f'{SERVICE_URL}/sentences/additional', method="GET") # this will make the method "POST"
    response = request.urlopen(req)
    return json.loads(response.read())

def normalize_skill_name(skill_name):
    return skill_name.lower().replace(" ", "").replace("-", "").replace("*", "").replace("/", "").replace(".", "").strip()


skills = get_skills()
edges = []

norm_map = {}
for skill_name in skills:
    norm_map[normalize_skill_name(skill_name)] = skill_name

skill_count = {}
for skill_name in skills:
    skill_data = skills[skill_name]
    parent = skill_data["parent"]
    if parent is None:
        continue
    if type(parent) != list:
        parent = [parent]
    for item in parent:
        if item not in norm_map:
            print(f"[skill-mismatch]: {item}")
            exit(0)
    skill_count[skill_name] = 0


additional_sentences = get_additional_sentences()
for sentence in additional_sentences:
    relations = sentence["relation"]
    for relation in relations:
        skill_name = norm_map[relation]
        skill_count.setdefault(skill_name, 0)
        skill_count[skill_name] += 1

skill_count_arr = []
for skill_name in skill_count:
    skill_count_arr.append({ "skill": skill_name, "count": skill_count[skill_name] })

skill_count_arr = sorted(skill_count_arr, key=lambda x: x["count"], reverse=True)
print("\n".join([ f'{item["skill"]}: {item["count"]}' for item in skill_count_arr ]))