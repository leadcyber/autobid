import re
import json
from skill.utils import get_required_skills
from functools import reduce

FITLEVEL_POSITION_PATH = "/Volumes/Data/local_db/fitlevel_position.json"
FITLEVEL_CONTENT_PATH = "/Volumes/Data/local_db/fitlevel_content.json"
SKILL_PATH = "/Volumes/Data/local_db/skills.yaml"


def get_title_score(title: str, fit_level: any):
    sum = 0
    for reg in fit_level["weight"]:
        match = re.search(reg, title, flags=re.IGNORECASE)
        if match is None:
            sum += fit_level["unknown"]
        else:
            sum += int(fit_level["weight"][reg])
    return sum

def is_proper_job_title(title: str):
    fit_level_file = open(FITLEVEL_POSITION_PATH)
    fit_level = json.load(fit_level_file)
    fit_level_file.close()
    return get_title_score(title, fit_level) >= fit_level["level"]

def is_proper_job_detail(detail: str):
    required_skills = get_required_skills(detail)
    if len(required_skills) == 0: return False
    importance_sorted = sorted(required_skills, key=lambda x: x["importance"], reverse=True)[:5]
    familarity_sorted = sorted(required_skills, key=lambda x: x["familarity"], reverse=True)[:5]
    selected_skills = reduce(lambda re, x: re+[x] if x not in re else re, importance_sorted + familarity_sorted, [])
    score = sum([ skill["familarity"] * skill["importance"] for skill in selected_skills ]) / len(selected_skills)
    # print("score", score)
    return score >= 35