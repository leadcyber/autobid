from docx import Document
from docx2pdf import convert

import re
import yaml
from utils.job_parser import get_required_skills, get_skill_occurence_matrix, compile_skill_tree, get_skill_relation_value, normalize_skill_name, get_allowed_nodes, select_skill_section_items
from config.config import WORKSPACE_PATH, DEFAULT_RESUME_PATH, DEFAULT_COVER_LETTER_PATH, LOG_RESUME_PATH, PY_SERVICE_URL
from utils.db import job_collection
from bson.objectid import ObjectId
import uuid
from datetime import datetime
import os
import shutil
from pathlib import Path
import math
from urllib import request, parse
import json

from utils import debugger

RESUME_TEMPLATE_PATH = f'{WORKSPACE_PATH}/resume'

def get_most_relevant_headline(position: str) -> str:
    request_body = parse.urlencode({
        "position": position,
        "jd": ""
    }).encode()
    req = request.Request(f'{PY_SERVICE_URL}/resume/generate/metadata', data=request_body) # this will make the method "POST"
    response = request.urlopen(req)
    response_json = json.loads(response.read())
    return response_json["headline"]

def generate_resume_by_data(position: str, description: str, job_id: str = "") -> str:
    result_filename = job_id if job_id != "" else f'resume-{datetime.now().strftime("%d-%m-%Y %H-%M-%S")}'
    result_filepath = os.path.abspath(f'{LOG_RESUME_PATH}/{result_filename}.docx')
    request_body = json.dumps({
        "position": position,
        "jd": description,
        "path": result_filepath
    }).encode()
    req = request.Request(f'{PY_SERVICE_URL}/resume/generate/file', data=request_body) # this will make the method "POST"
    req.add_header('Content-Type', 'application/json')
    response = request.urlopen(req)
    response.read()
    return result_filepath

def generate_cover_letter_by_data(platform: str, position: str, description: str, job_id: str = "") -> str:
    pass

def generate_resume_by_id(job_id: str) -> str:
    # Query job data
    if job_id == "":
        return DEFAULT_RESUME_PATH
    job = job_collection.find_one({"_id": ObjectId(job_id), "pageData": {"$not": {"$eq": None}}})
    if job is None:
        return DEFAULT_RESUME_PATH
    # Get template resume
    page_data = job["pageData"]
    position = job["position"]
    description = page_data["description"]
    return generate_resume_by_data(position, description, job_id)

def generate_cover_letter_by_id(platform:str, job_id: str) -> str:
    # Query job data
    if job_id == "":
        return DEFAULT_COVER_LETTER_PATH
    job = job_collection.find_one({"_id": ObjectId(job_id), "pageData": {"$not": {"$eq": None}}})
    if job is None:
        return DEFAULT_COVER_LETTER_PATH
    # Get template resume
    page_data = job["pageData"]
    position = job["position"]
    description = page_data["description"]
    return generate_cover_letter_by_data(platform, position, description, job_id)