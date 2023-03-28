from skill.utils import get_skill_list, get_required_skill_groups, get_required_skills
import re
import math
from .config import MAX_SEQUENCE_LENGTH

alternative = {
    "spa-framework": "singlepageapplication",
    "ethersjs": "ethers",
    "nestjs": "expressjs",
    "design-system": "design",
    "design-tool": "design",
    "collaboration-tool": "collaboration",
    "frontend-architecture": "frontend",
    "backend-architecture": "architecture",
    "daily-standup": "standup",
    "react-testing-library": "jest",
    "fast-api": "flask",
    "vercel": "netlify",
    "uniswap": "ethereum",
    "frontend-optimization": "frontend",
    "pinia": "vuex",
    "cloud-functions": "azure",
    "cloud-datastore": "azure",
    "azure-files": "azure",
    "chakra-ui": "chakra",
    "uiux": "ui"
}

def get_title_score(title: str, fit_level: any):
    sum = 0
    for reg in fit_level["weight"]:
        match = re.search(reg, title, flags=re.IGNORECASE)
        if match is None:
            sum += fit_level["unknown"]
        else:
            sum += int(fit_level["weight"][reg])
    return sum
def get_jd_score(detail: str):
    required_skills = get_required_skills(detail)
    if len(required_skills) == 0:
        return False
    fsum = 0
    fcount = 0
    for skill in required_skills:
        fsum += skill["familarity"] * math.sqrt(skill["importance"] / 10)
        fcount += math.sqrt(skill["importance"] / 10)
    return fsum / fcount


def predetermine_jd_fitness(jd: str):
    score = get_jd_score(jd)
    if score >= 7.5:
        return True
    if score <= 4.8:
        return False
    return None

def to_understandable_skill_name(full_name):
    skill_name = full_name.lower().replace(" ", "-").replace(".", "")
    if skill_name in alternative:
        skill_name = alternative[skill_name]
    return skill_name

def get_understandable_skill_list():
    skills = get_skill_list()
    skill_name_list = []
    for index, full_name in enumerate(skills):
        skill_name = to_understandable_skill_name(full_name)
        skill_name_list.append(skill_name)
    return list(set(skill_name_list))

def get_required_skill_index_sequence(jd: str, skill_name_list):
    groups = get_required_skill_groups(jd)
    occurences = [ to_understandable_skill_name(item["skillName"]) for sub_list in groups for item in sub_list ]
    index_occurences = [ skill_name_list.index(occurence) + 1 for occurence in occurences ]
    if len(index_occurences) < MAX_SEQUENCE_LENGTH:
        index_occurences.extend([0] * (MAX_SEQUENCE_LENGTH - len(index_occurences)))
    else:
        index_occurences = index_occurences[0:MAX_SEQUENCE_LENGTH]
    return index_occurences
