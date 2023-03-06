from db import job_collection
from skill.utils import get_required_skill_groups, get_skill_list
import yaml

jobs = job_collection.find({"pageData.description": {"$not": {"$eq": None}}})
embed = {}
skills = get_skill_list()
for skill_name in skills:
    embed[skill_name] = {}
count = 0
for job in jobs:
    count += 1
    print(count)
    description = job["pageData"]["description"]
    groups = get_required_skill_groups(description)
    occurences = [item for sub_list in groups for item in sub_list]
    required_skills_set = set([ occurence["skillName"] for occurence in occurences ])
    required_skills = list(required_skills_set)
    in_group_weight = 0.2
    out_group_weight = 1
    for required_skill in required_skills:
        in_group_count = 0
        out_group_count = 0
        for target_skill in required_skills:
            if required_skill == target_skill:
                continue
            out_group_count += 1
            for group in groups:
                if required_skill in [ item["skillName"] for item in group ] and \
                    target_skill in [ item["skillName"] for item in group ]:
                    in_group_count += 1
            embed[required_skill].setdefault(target_skill, 0)
            embed[required_skill][target_skill] += (1.0 - 0.5 ** in_group_count) * in_group_weight
            embed[required_skill][target_skill] += (1.0 - 0.5 ** out_group_count) * out_group_weight
    
with open('/Volumes/Data/local_db/skill_occurence.yaml', 'w') as file:
    documents = yaml.dump(embed, file)

import job_familarity_model.test_vector_existence
import job_familarity_model.train_model