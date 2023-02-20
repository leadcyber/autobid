from threading import local
import yaml
from config import config
import re
from datetime import date

from utils.resume import generate_resume_by_id, generate_cover_letter_by_id

def load_answers(file_name: str):
    common_global_answers = None
    global_answers = None
    common_local_answers = None
    local_answers = None

    try:
        with open(f'./db/qa/common/_common.yaml', "r") as stream:
            common_global_answers = yaml.safe_load(stream) or {}
    except:
        common_global_answers = {}

    try:
        with open(f'./db/qa/common/{file_name}.yaml', "r") as stream:
            global_answers = yaml.safe_load(stream) or {}
    except:
        global_answers = {}

    try:
        with open(f'./db/qa/common/{config.current_profile_id}/_common.yaml', "r") as stream:
            common_local_answers = yaml.safe_load(stream) or {}
    except:
        common_local_answers = {}

    try:
        with open(f'./db/qa/common/{config.current_profile_id}/{file_name}.yaml', "r") as stream:
            local_answers = yaml.safe_load(stream) or {}
    except:
        local_answers = {}
    

    res = common_global_answers
    res.update(global_answers)
    res.update(common_local_answers)
    res.update(local_answers)
    return res

def get_skill_matrix():
    skill_matrix = {}
    try:
        with open(f'./db/qa/skill/skill_matrix.yaml', "r") as stream:
            skill_matrix = yaml.safe_load(stream) or {}
    except:
        skill_matrix = {}
    original_keys = list(skill_matrix.keys())
    for key in original_keys:
        splits = key.split("|")
        value = skill_matrix[key]
        del skill_matrix[key]
        for sp in splits:
            skill_matrix[sp.lower()] = value
    return skill_matrix

def is_resume_question(question):
    if re.search("resume", question, re.IGNORECASE):
        return True
    return False
def is_cover_letter_question(question):
    if re.search("cover letter", question, re.IGNORECASE):
        return True
    if re.search("Your message to", question, re.IGNORECASE):
        return True
    return False

def get_skill_answer(question: str):
    def get_skill_reg(skill: str):
        return skill.replace("+", "\\+")
    skill_matrix = get_skill_matrix()
    questions = sorted(list(skill_matrix.keys()), key=len, reverse=True)
    if question in questions:
        return skill_matrix[question]

    if re.search("Do (you )?have(.*?)(experience|knowledge|expertise|proven(.*?)(competen|skill)|proficiency) (in|with|of|on)", question, re.IGNORECASE):
        return "Yes"
    if re.search("(Solid|in-depth) understanding of(.*?)", question, re.IGNORECASE):
        return "Yes"
    if re.search("Do you have(.*?)years of(.*?)(experience|work)", question, re.IGNORECASE):
        return "Yes"
    if re.search("^Do you have(.*?)experience", question, re.IGNORECASE):
        return "Yes"
    if re.search("^Are you proficient (in|with)", question, re.IGNORECASE):
        return "Yes"
    for skill in skill_matrix:
        possibles = [ get_skill_reg(skill) ]
        skill_value = skill_matrix[skill]

        skill_with_dash = skill.replace(" ", "-")
        if skill_with_dash != skill:
            possibles.append(get_skill_reg(skill_with_dash))
        skill_without_space = skill.replace(" ", "")
        if skill_without_space != skill:
            possibles.append(get_skill_reg(skill_without_space))
        skill_without_dot = skill.replace(".", "")
        if skill_without_dot != skill:
            possibles.append(get_skill_reg(skill_without_dot))
        
        skill_reg = f"({'|'.join(possibles)})"
        if re.search(f"Total exp(.*?) (in|with|of)(.*?){skill_reg}", question, re.IGNORECASE) or \
            re.search(f"years(.*?)exp(.*?) (using|with|in|related|as|on|writ)(.*?) {skill_reg}", question, re.IGNORECASE) or \
            re.search(f"years(.*?) {skill_reg}(.*?)(exp|engineer|development)(.*?)you(.*?)have", question, re.IGNORECASE) or \
            re.search(f"years(.*?) {skill_reg}(.*?)experience$", question, re.IGNORECASE) or \
            re.search(f"years do you have (using|with|in|related|as|on) {skill_reg}", question, re.IGNORECASE) or \
            re.search(f"how long(.*?)work(.*?){skill_reg}", question, re.IGNORECASE):
            return str(skill_value[0])
        
        if re.search(f"you have(.*?)(understanding|exp|skill)(.*?)(with|:)(.*?) {skill_reg}", question, re.IGNORECASE):
            return True

        if re.search(f"What is your(.*?)exp(.*?){skill_reg}", question, re.IGNORECASE) is not None or \
            re.search(f"Describe your(.*?)exp(.*?){skill_reg}", question, re.IGNORECASE) or \
            re.search(f"^exp(.*?)with(.*?){skill_reg}", question, re.IGNORECASE):
            return f"I have around {skill_value[0]} year{'s' if skill_value[0] > 1 else ''} of professional experience with {skill_value[1]}."

    if re.search("You have(.*?)(understanding|exp)(.*?)with", question, re.IGNORECASE) or \
        re.search("In which(.*?)(are|do) you(.*?)(proficient)", question, re.IGNORECASE) or \
        re.search("tell(.*?)if you have(.*?)exp(.*?)following area", question, re.IGNORECASE):
        return list(skill_matrix.keys())
    return None

def _get_answer(platform: str, question: str, job_id: str):
    if platform == "bamboohr" and question == "Date Available":
        today = date.today()
        return "%02d/%02d/%04d" % (today.month, today.day, today.year)
    if platform == "lever" and re.search("Today’s date", question, re.IGNORECASE):
        today = date.today()
        return "%02d/%02d/%04d" % (today.month, today.day, today.year)
    if re.search("today", question, re.IGNORECASE):
        today = date.today()
        return "%02d/%02d/%04d" % (today.month, today.day, today.year)

    question = normalize_text(question)

    if is_resume_question(question):
        return generate_resume_by_id(job_id)
    # if is_cover_letter_question(question):
    #     return generate_cover_letter_by_id(platform, job_id)
    
    skill_answer = get_skill_answer(question)
    if skill_answer is not None:
        return skill_answer

    answers = load_answers(platform)
    if question in answers:
        return answers[question]
    if question.capitalize() in answers:
        return answers[question.capitalize()]
    if question.lower() in answers:
        return answers[question.lower()]
    if question.upper() in answers:
        return answers[question.upper()]
    if question.title() in answers:
        return answers[question.title()]
    
    result = None
    for qus in filter(lambda x: x.startswith('!!!'), answers):
        matches = re.search(qus[3:], question, re.IGNORECASE)
        if matches is not None:
            print("regex-not: ", qus)
            return ""
    for qus in filter(lambda x: x.startswith('///'), answers):
        matches = re.search(qus[3:], question, re.IGNORECASE)
        if matches is None:
            continue

        answer_pattern = answers[qus]
        for i, match in enumerate(matches.groups()):
            if match is None:
                continue
            if type(answer_pattern) == str:
                answer_pattern = answer_pattern.replace(f'**{i + 1}**', match)
            elif type(answer_pattern) == list:
                for ans_index in range(len(answer_pattern)):
                    if type(answer_pattern[ans_index]) == str:
                        answer_pattern[ans_index] = answer_pattern[ans_index].replace(f'**{i + 1}**', match)
        print("regex: ", qus)
        if result is None:
            result = answer_pattern
        elif type(result) == list:
            if type(answer_pattern) == list:
                result.extend(answer_pattern)
            else:
                result.append(answer_pattern)
        else:
            if type(answer_pattern) == list:
                result = [result]
                result.extend(answer_pattern)
            else:
                result = [result, answer_pattern]
    return result

def get_answer(platform: str, question: str, job_id: str = ""):
    answer = _get_answer(platform, question, job_id)
    if answer is None:
        return None
    if type(answer) != list:
        return [ answer ]
    return answer

def is_correct_answer(current, sample):
    if type(sample) == str:
        sample = [ sample ]
    if type(sample) == bool:
        if sample is True:
            sample = [ "///Yes", "///(acknowledge|confirm|consent)" ]
        else:
            sample = [ "No", "///^No" ]
    current = normalize_text(current)
    for ans in sample:
        if ans is True:
            return True
        if type(ans) != str:
            continue
        if ans.startswith("!!!"):
            matches = re.search(ans[3:], current, re.IGNORECASE)
            if matches is not None:
                return False
        if ans.startswith("///"):
            matches = re.search(ans[3:], current, re.IGNORECASE)
            if matches is not None:
                return True
        elif current == normalize_text(ans):
            return True
        
        if "$" not in current:
            try:
                current_value = float(ans)
                range_match = re.search("([0-9.]+)(.*?)-(.*?)([0-9.]+)", current)
                if range_match is not None:
                    range_start = range_match.group(1)
                    range_end = range_match.group(4)
                    if current_value >= float(range_start) and current_value <= float(range_end):
                        return True
                range_match = re.search("([0-9.]+)\\+", current)
                if range_match is not None:
                    range_start = range_match.group(1)
                    if current_value >= float(range_start):
                        return True
                range_match = re.search(">([0-9.]+)", current)
                if range_match is not None:
                    range_start = range_match.group(1)
                    if current_value >= float(range_start):
                        return True
            except: pass
            
    return False

def normalize_text(text: str) -> str:
    return text.lower().replace("&nbsp;", "").replace("’", "'").replace("*", "").replace("(optional)", "").strip()

def is_money_str(text: str) -> bool:
    if text.startswith("$"):
        return True
    return False

def money_str2num(text: str) -> str:
    text = text.replace("$", "")
    text = text.replace("/yr", "")
    text = text.replace("/hr", "")
    text = text.replace("k", "000")
    text = text.replace("K", "000")
    return text

def find_exact_question(text: str) -> str:
    lines = text.split("\n")
    lines = list(filter(lambda line: len(line) > 0, lines))
    if len(lines) == 0: return None
    if len(lines) == 1: return lines[0]

    unavailable_pattern = "(The following demographic information encompasses)"
    if re.search(unavailable_pattern, lines[0], re.IGNORECASE) is None:
        return lines[0]
    if re.search(unavailable_pattern, lines[-1], re.IGNORECASE) is None:
        return lines[-1]
    return None