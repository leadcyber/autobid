from utils.job_parser import get_required_skills
with open("./test/page_data.txt") as f:
    data = f.read()
    required_skills = get_required_skills(data)
    for skill in required_skills:
        print(skill["skill"], skill["importance"])