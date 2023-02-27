from skill.utils import normalize_skill_name, get_allowed_nodes, get_skill_occurence_matrix
from skill.skill_tree import get_skill_tree, get_skill_relation_value
from .utils import get_most_relevant_template, select_skill_section_items


def generate_detailed_skill_matrix(position: str, required_skills):
    (root, nodes) = get_skill_tree()
    template_type = get_most_relevant_template(position, required_skills)

    levels = {}
    for skill_name in nodes:
        level = nodes[skill_name].data["level"]
        levels[skill_name] = level

    # Generate skill section
    length_more = {}
    if template_type in ["react", 'vue', 'angular']:
        length_more = { "frontend": 25, "backend": -10, "database": -10 , "cloud": -10, "dev": 5, "mobile": 5, "blockchain": -10 }
    elif template_type in [ "fullstack" ]:
        length_more = { "frontend": 5, "backend": 10, "database": 0 , "cloud": 0, "dev": 0, "mobile": -4, "blockchain": -10 }
    else:
        length_more = { "frontend": 0, "backend": 10, "database": 5 , "cloud": 10, "dev": 5, "mobile": -5, "blockchain": -10 }
    
    skill_category_info = {
        "frontend": { "score": 0.3, "skills": [], "fullname": "Front-End Development", "length": 37 + length_more["frontend"], "scale": 1.5, "default": ["React"] },
        "backend":  { "score": 0.2, "skills": [], "fullname": "Back-End Development", "length": 35 + length_more["backend"], "scale": 1, "default": ["Node"] },
        "dev":      { "score": 0.1, "skills": [], "fullname": "Development Management", "length": 20 + length_more["dev"], "scale": 0.3, "default": ["Agile"] },
        "cloud":    { "score": 0, "skills": [], "fullname": "Cloud Development", "length": 30 + length_more["cloud"], "scale": 0.8, "default": ["AWS"] },
        "database": { "score": 0, "skills": [], "fullname": "DB Administration", "length": 30 + length_more["database"], "scale": 0.7, "default": ["MySQL"] },
        "mobile":   { "score": 0, "skills": [], "fullname": "Mobile Development", "length": 20 + length_more["mobile"], "scale": 0.7, "default": ["React Native"] },
        "blockchain":   { "score": 0, "skills": [], "fullname": "Blockchain Development", "length": 20 + length_more["blockchain"], "scale": 0.7, "default": ["Web3"] }
    }

    for required_skill in required_skills:
        norm_skill = normalize_skill_name(required_skill["skill"])
        max_category = { "score": 0, "category": "" }
        for category in skill_category_info:
            score = get_skill_relation_value(required_skill["skill"], category, nodes, 0.1) * required_skill["importance"]
            skill_category_info[category]["score"] += score * skill_category_info[category]["scale"]
            if max_category["score"] < score:
                max_category = { "score": score, "category": category }
        skill_category_info[max_category["category"]]["skills"].append(required_skill["skill"])
    skill_categories = sorted([ (skill_category_info[item]["score"], item) for item in skill_category_info ], key=lambda x: x[0], reverse=True)
    # print(skill_categories)
    skill_section_headers = []
    skill_section_contents = []

    print(skill_categories)

    banned_skill_names_more = []
    for index, skill_category_name in enumerate(skill_categories):
        norm_category_name = normalize_skill_name(skill_category_name[1])
        base_skill_full_names = skill_category_info[norm_category_name]["skills"]
        category_score = skill_category_info[norm_category_name]["score"]
        if (index > 2 and category_score == 0) or index == 5:
            break

        if len(base_skill_full_names) == 0:
            base_skill_full_names = skill_category_info[norm_category_name]["default"]
        category_length = skill_category_info[norm_category_name]["length"]
        base_skills = list(map(normalize_skill_name, filter(lambda x: levels[normalize_skill_name(x)] >= 0, base_skill_full_names)))
        banned_skill_names = list(filter(lambda x: x != norm_category_name, skill_category_info.keys())) + banned_skill_names_more
        allowed_nodes = get_allowed_nodes(norm_category_name, banned_skill_names, nodes)
        available_nodes = [ nodes[skill_name] for skill_name in base_skills ]
        
        selected_skills = []
        (_selected_skills, line_length) = select_skill_section_items(available_nodes)
        if line_length > category_length:
            selected_skills = _selected_skills
        else:
            o_matrix = get_skill_occurence_matrix()
            candidates = {}
            for full_skill_name in base_skill_full_names:
                candidates[full_skill_name] = []
                relations = o_matrix[full_skill_name]
                for relation in relations:
                    candidates[full_skill_name].append((relation, relations[relation]))
                candidates[full_skill_name].sort(key=lambda x: x[1], reverse=True)
            depth = 0
            while True:
                max_depth_reached = True
                for full_skill_name in base_skill_full_names:
                    if depth >= len(candidates[full_skill_name]):
                        continue
                    max_depth_reached = False
                    candidate_skill_name = candidates[full_skill_name][depth][0]
                    candidate_node = nodes[normalize_skill_name(candidate_skill_name)]
                    if candidate_node in allowed_nodes and candidate_node not in available_nodes:
                        available_nodes.append(candidate_node)
                (_selected_skills, line_length) = select_skill_section_items(available_nodes)
                if line_length > category_length or max_depth_reached:
                    selected_skills = _selected_skills
                    break
                depth += 1
        selected_skills.sort(key=lambda x: nodes[normalize_skill_name(x)].data["level"], reverse=True)
        banned_skill_names_more.extend(list(map(normalize_skill_name, selected_skills)))
        skill_section_headers.append({
            "label": skill_category_info[norm_category_name]["fullname"],
            "score": skill_category_info[norm_category_name]["score"]
        })
        skill_section_contents.append({
            "skills": selected_skills
        })
    return skill_section_headers, skill_section_contents

def generate_skill_matrix(position: str, required_skills):
    skill_section_headers, skill_section_contents = generate_detailed_skill_matrix(position, required_skills)
    return [ item["label"] for item in skill_section_headers ], [ item["skills"] for item in skill_section_contents ]