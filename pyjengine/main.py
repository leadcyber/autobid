from flask import Flask, request
from flask_cors import CORS

import resume
import emailparser
import json
from skill.utils import get_required_skills
from config import PY_SERVICE_PORT
from job_familarity_model.prediction import is_proper_position, is_proper_jd, get_jd_rate
from job_familarity_model.utils import get_jd_score

app = Flask(__name__)
CORS(app)

@app.post("/job/score")
def get_job_score():
    body = json.loads(request.data)
    jd = body["jd"]
    return {"score": get_jd_score(jd) }

@app.post("/job/rate")
def get_job_rate():
    body = json.loads(request.data)
    jd = body["jd"]
    return {"rate": get_jd_rate(jd) }

@app.post("/job/autobiddable")
def is_autobiddable():
    body = json.loads(request.data)
    position = body["position"]
    jd = body["jd"]
    print(position)
    return {"available": is_proper_position(position) and is_proper_jd(jd) }

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
    headline, summary, positions = resume.generate_meta_data(body["position"], required_skills)
    return {
        "headline": headline,
        "summary": summary,
        "positions": positions
    }



@app.post("/resume/generate/skillmatrix")
def generate_resume_skill_matrix():
    body = json.loads(request.data)
    required_skills = get_required_skills(body["jd"])
    skill_section_headers, skill_section_contents = resume.generate_skill_matrix(body["position"], required_skills)
    sections = []
    for index, header in enumerate(skill_section_headers):
        sections.append({ "header": header, "content": skill_section_contents[index] })
    return sections

@app.post("/resume/generate/skillmatrix/detail")
def generate_resume_detailed_skill_matrix():
    body = json.loads(request.data)
    required_skills = get_required_skills(body["jd"])
    skill_section_headers, skill_section_contents = resume.generate_detailed_skill_matrix(body["position"], required_skills)
    sections = []
    for index, header in enumerate(skill_section_headers):
        sections.append({ "header": header, "content": skill_section_contents[index] })
    return sections




@app.post("/resume/generate/sentences")
def generate_resume_sentences():
    body = json.loads(request.data)
    required_skills = get_required_skills(body["jd"])
    sentences = resume.generate_resume_sentences(body["position"], required_skills)
    return sentences

@app.post("/resume/generate/sentences/detail")
def generate_detailed_resume_sentences():
    body = json.loads(request.data)
    required_skills = get_required_skills(body["jd"])
    sentences = resume.generate_detailed_resume_sentences(body["position"], required_skills)
    return sentences



@app.post("/resume/generate/file")
def generate_resume_file():
    body = json.loads(request.data)
    required_skills = get_required_skills(body["jd"])
    resume.generate_resume_file(body["position"], required_skills, body["path"])
    return ""

app.run(port=PY_SERVICE_PORT)