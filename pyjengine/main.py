from flask import Flask, request
from job import is_proper_job_title
import resume
import emailparser
import json
from skill.utils import get_required_skills
from config import PY_SERVICE_PORT

app = Flask(__name__)

@app.route("/job/proper")
def is_proper_job_title(title: str):
    return is_proper_job_title(title)

@app.post("/email/parse/company")
def parse_company_name():
    body = json.loads(request.data)
    print(body["sentence"])
    company_names = emailparser.parse_company_name(body["sentence"])
    return { "company": company_names }



@app.post("/resume/generate/metadata")
def generate_resume_metadata():
    body = json.loads(request.data)
    required_skills = get_required_skills(body["jd"])
    return resume.generate_meta_data(body["position"], required_skills)

@app.post("/resume/generate/sentences")
def generate_resume_sentences():
    body = json.loads(request.data)
    required_skills = get_required_skills(body["jd"])
    return resume.generate_resume_sentences(body["position"], required_skills)

@app.post("/resume/generate/skillmatrix")
def generate_resume_skill_matrix():
    body = json.loads(request.data)
    required_skills = get_required_skills(body["jd"])
    resume.generate_skill_matrix(body["position"], required_skills)

@app.post("/resume/generate/file")
def generate_resume_file():
    body = json.loads(request.data)
    required_skills = get_required_skills(body["jd"])
    resume.generate_resume_file(body["position"], required_skills, body["path"])
    return ""

app.run(port=PY_SERVICE_PORT)