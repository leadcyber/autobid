import db
from skill.utils import get_skill_list, get_required_skill_groups, get_required_skills, normalize_skill_name
from resume.sentences import generate_resume_sentences
from job_familarity_model.word2vec import similarity_nm

jobs = list(db.job_collection.find({"pageData.description": {"$not": {"$eq": None}}}))
similarities = []
for index, job in enumerate(jobs):
    position = job["position"]
    description = job["pageData"]["description"]

    groups = get_required_skill_groups(description, position)
    occurences1 = [ normalize_skill_name(item["skillName"]) for sub_list in groups for item in sub_list ]

    required_skills = get_required_skills(description, position)
    sentences = generate_resume_sentences(position, required_skills, description)

    r_description = "\n".join([ f"<p>{sentence}</p>" for sentence in sentences ])
    groups = get_required_skill_groups(r_description, position)
    occurences2 = [ normalize_skill_name(item["skillName"]) for sub_list in groups for item in sub_list ]

    similarity = similarity_nm(occurences1, occurences2)
    similarities.append(similarity)
    print(index, similarity)
    if index == 200:
        break

print("Average: ", sum(similarities) / len(similarities))
    