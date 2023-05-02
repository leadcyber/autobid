from urllib import request, parse
from autobid.env import JS_SERVICE_URL
import json
from functools import reduce

def normalize_skill_name(skill_name):
    return skill_name.lower().replace(" ", "").replace("-", "").replace("*", "").replace("/", "").replace(".", "").strip()


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


def get_skill_list():
    req = request.Request(f'{JS_SERVICE_URL}/skill/list', method="GET") # this will make the method "POST"
    response = request.urlopen(req)
    return json.loads(response.read())

def get_skill_occurence_matrix():
    req = request.Request(f'{JS_SERVICE_URL}/skill/occurence/matrix', method="GET") # this will make the method "POST"
    response = request.urlopen(req)
    return json.loads(response.read())


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