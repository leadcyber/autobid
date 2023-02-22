from urllib import request, parse
from config import SERVICE_URL
import json

def get_skill_list():
    req = request.Request(f'{SERVICE_URL}/skill/list', method="GET") # this will make the method "POST"
    response = request.urlopen(req)
    return json.loads(response.read())

def get_required_skill_groups(jd: str):
    request_body = parse.urlencode({"jd": jd}).encode()
    req = request.Request(f'{SERVICE_URL}/skill/measure/groups', data=request_body) # this will make the method "POST"
    response = request.urlopen(req)
    return json.loads(response.read())