import db
from skill.utils import get_skill_list, get_required_skill_groups, get_required_skills, normalize_skill_name
from resume.sentences import generate_resume_sentences
from job_familarity_model.word2vec import similarity_nm
import re

print("Input regexp of the target sentence:")
query = input()

jobs = list(db.job_collection.find({"pageData.description": {"$not": {"$eq": None}}}))
similarities = []
for index, job in enumerate(jobs):
    position = job["position"]
    description = job["pageData"]["description"]

    required_skills = get_required_skills(description)
    sentences = generate_resume_sentences(position, required_skills, description)

    found = False
    for sentence in sentences:
        match = re.search(query, sentence, flags=re.IGNORECASE)
        if match is not None:
            found = True
            break
    print(job["_id"], job["position"], job["company"])

print("Average: ", sum(similarities) / len(similarities))
    