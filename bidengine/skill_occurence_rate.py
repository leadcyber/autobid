from utils import db
from utils.job_parser import get_required_skill_groups, get_skill_list
import yaml

jobs = db.job_collection.find({"pageData.description": {"$not": {"$eq": None}}, "alreadyApplied": True})
skills = get_skill_list()
embed = {}
for skill_name in skills:
    embed[skill_name] = 0
count = 0
for job in jobs:
    count += 1
    print(count)
    description = job["pageData"]["description"]
    position = job["position"]
    groups = get_required_skill_groups(description, position)
    occurences = [item for sub_list in groups for item in sub_list]
    required_skills_set = set([ occurence["skillName"] for occurence in occurences ])
    required_skills = list(required_skills_set)
    for required_skill in required_skills:
        embed[required_skill] += 1
counts = [ (skill, embed[skill]) for skill in embed ]
counts.sort(key=lambda x: x[1], reverse=True)
print(counts)