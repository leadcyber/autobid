from logging.handlers import RotatingFileHandler
from nis import match
import re
import json
from functools import reduce
from urllib import request, parse
from autobid.env import WORKSPACE_PATH, JS_SERVICE_URL

FITLEVEL_POSITION_PATH = f"{WORKSPACE_PATH}/fitlevel_position.json"
FITLEVEL_CONTENT_PATH = f"{WORKSPACE_PATH}/fitlevel_content.json"
SKILL_PATH = f"{WORKSPACE_PATH}/skills.yaml"

def normalize_skill_name(skill_name):
    return skill_name.lower().replace(" ", "").replace("-", "").replace("*", "").replace("/", "").replace(".", "").strip()
class SkillNode:
    def __init__(self, skill_name="", data=None, parents=[], children=[]) -> None:
        self.data = data
        self.skill_name = skill_name
        self.parents = parents.copy()
        self.children = children.copy()

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

def get_skill_list():
    req = request.Request(f'{JS_SERVICE_URL}/skill/list', method="GET") # this will make the method "POST"
    response = request.urlopen(req)
    return json.loads(response.read())

def get_skill_occurence_matrix():
    req = request.Request(f'{JS_SERVICE_URL}/skill/occurence/matrix', method="GET") # this will make the method "POST"
    response = request.urlopen(req)
    return json.loads(response.read())

def get_required_skills(jd: str):
    request_body = parse.urlencode({"jd": jd}).encode()
    req = request.Request(f'{JS_SERVICE_URL}/skill/measure', data=request_body) # this will make the method "POST"
    response = request.urlopen(req)
    return json.loads(response.read())

def get_required_skill_groups(jd: str):
    request_body = parse.urlencode({"jd": jd}).encode()
    req = request.Request(f'{JS_SERVICE_URL}/skill/measure/groups', data=request_body) # this will make the method "POST"
    response = request.urlopen(req)
    return json.loads(response.read())

def compile_skill_tree():
    skills = get_skill_list()
    root = SkillNode()
    nodes = {}
    normalized = {}
    
    def compile_skill_item(skill_name):
        normalized_skill_name = normalize_skill_name(skill_name)
        skill_data = skills[skill_name]
        if normalized_skill_name in nodes:
            return nodes[normalized_skill_name]
        
        node = SkillNode(skill_name, skill_data)
        nodes[normalized_skill_name] = node
        if skill_data["parent"] is None:
            root.children.append(node)
            node.parents.append(root)
        elif type(skill_data["parent"]) == str:
            parent_node = compile_skill_item(normalized[skill_data["parent"]])
            node.parents.append(parent_node)
            parent_node.children.append(node)
        else:
            for parent_name in skill_data["parent"]:
                parent_node = compile_skill_item(normalized[parent_name])
                node.parents.append(parent_node)
                parent_node.children.append(node)
        return node
    
    for skill_name in skills:
        normalized[normalize_skill_name(skill_name)] = skill_name
    
    for skill_name in skills:
        compile_skill_item(skill_name)
    return (root, nodes)

def get_allowed_nodes(root_skill_name, banned_skill_names, nodes):
    def _iterate_children(root_node, banned_nodes) -> list:
        allowed_nodes = [ root_node ]
        for child_skill in root_node.children:
            child_skill_name = normalize_skill_name(child_skill.skill_name)
            if child_skill_name in banned_skill_names:
                continue
            allowed_nodes.extend(_iterate_children(nodes[child_skill_name], banned_nodes))
        return allowed_nodes
    return _iterate_children(nodes[root_skill_name], [ nodes[skill_name] for skill_name in banned_skill_names ])

def get_skill_relation_value(skill_name: str, target_skill_name: str, nodes, parent_loss=0.4, child_loss=0.2):
    normalized = normalize_skill_name(skill_name)
    def _get_skill_depth(node: SkillNode, target_skill_name: str, get_connections):
        if normalize_skill_name(node.skill_name) == target_skill_name:
            return [1]
        connections = get_connections(node)
        for connection in connections:
            depths = _get_skill_depth(connection, target_skill_name, get_connections)
            if depths is not None:
                return depths + [len(connections)]
        return None
    depths = _get_skill_depth(nodes[normalized], target_skill_name, lambda x: x.children)
    discord_limit = 0
    if depths is None:
        depths = _get_skill_depth(nodes[normalized], target_skill_name, lambda x: x.parents)
        if depths is None:
            return 0
        else:
            discord_limit = parent_loss
    else:
        discord_limit = child_loss
    return 1 - (discord_limit - discord_limit ** reduce(lambda x, y: x + y, depths, 0))

def select_skill_section_items(nodes):
    selected_skills = []
    line_length = 0
    for node in nodes:
        if node.data["level"] >= 7:
            selected_skills.append(node.skill_name)
            line_length += len(node.skill_name)
    return (selected_skills, line_length)