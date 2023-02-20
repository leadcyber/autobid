import re
from config import WORKSPACE_PATH


RESUME_TEMPLATE_PATH = f'{WORKSPACE_PATH}/resume'

def get_most_relevant_headline(position: str) -> str:
    if re.search("full(.*?)stack", position, re.IGNORECASE):
        return "Senior Full Stack Engineer"
    if re.search("(front(.*?)end)|react|angular|UI|UX|javascript|typescript|FE|Vue", position, re.IGNORECASE):
        return "Senior Front End Engineer"
    return "Senior Software Engineer"

def get_most_relevant_template(position: str, required_skills: any):
    if re.search("full(.*?)stack", position, re.IGNORECASE):
        return "fullstack"
    if re.search("(front(.*?)end)|react|angular|UI|UX|javascript|typescript|FE|Vue", position, re.IGNORECASE):
        if re.search("react", position, re.IGNORECASE):
            return "react"
        if re.search("angular", position, re.IGNORECASE):
            return "angular"
        if re.search("vue", position, re.IGNORECASE):
            return "vue"
        for required_skill in required_skills:
            if required_skill["skill"] == "React":
                return "react"
            if required_skill["skill"] == "Angular":
                return "angular"
            if required_skill["skill"] == "Vue":
                return "vue"
        return "react"
    return "software"

def select_skill_section_items(nodes):
    selected_skills = []
    line_length = 0
    for node in nodes:
        if node.data["level"] >= 7:
            selected_skills.append(node.skill_name)
            line_length += len(node.skill_name)
    return (selected_skills, line_length)