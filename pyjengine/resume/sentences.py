from skill.utils import normalize_skill_name, get_required_skill_groups
from skill.skill_tree import get_skill_tree, get_skill_relation_value
from .utils import get_most_relevant_template
from ._template import get_template_data
from ._sentencedb import get_sentence_db
from job_familarity_model.word2vec import similarity_nm
import re

LIMIT_YEARS = [
    2050, 2050, 2050, 2050, 2050,
    2021, 2021, 2021, 2021,
    2017, 2017, 2017, 2017,
    2014, 2014, 2014, 2014
]

def generate_sentences_from_template(template):
    exchange = template.get("exchange", {})
    sentences = []

    replacement = []

    def do_replacement(match_obj):
        nonlocal replacement
        value = replacement[0]
        replacement.pop(0)
        return value

    def _recursive_generate(content, relations, exchange_keys):
        nonlocal exchange, replacement, sentences
        if len(exchange_keys) == 0:
            sentences.append({
                "content": content,
                "relations": relations
            })
            return
        front_key = exchange_keys[0]
        keys_left = exchange_keys[1:]

        replacements = exchange[front_key]
        for rep in replacements:
            replacement = rep[0][:]
            replaced = re.sub("{" + front_key + "}", do_replacement, content)
            relation_ext = relations[:]
            relation_ext.extend(list(filter(lambda x: x is not None, rep[1])))
            _recursive_generate(replaced, relation_ext, keys_left)
    content = template["content"]
    relations = template["relations"]
    _recursive_generate(content, relations, list(exchange.keys()))
    return sentences
    
def generate_detailed_resume_sentences(position: str, required_skills, jd: str) -> str:
    (root, nodes) = get_skill_tree()
    template_type = get_most_relevant_template(position, required_skills)
    try:
        template = get_template_data(template_type)
    except:
        return None

    sentences = template["default_sentences"]
    final_sentences = []
    for sentence in sentences:
        final_sentences.append({
            "content": sentence["content"],
            "metadata": None
        })
    if len(required_skills) == 0:
        return final_sentences
    
    sentence_db = get_sentence_db()
    sentence_usage = [ False ] * len(sentence_db)


    skill_category_info = {
        "frontend": { "score": 0.03, "skills": [], "full_skills": [], "scale": 1.1 },
        "backend":  { "score": 0.02, "skills": [], "full_skills": [], "scale": 1 },
        "dev":      { "score": 0.01, "skills": [], "full_skills": [], "scale": 0.3 },
        "cloud":    { "score": 0, "skills": [], "full_skills": [], "scale": 1 },
        "database": { "score": 0, "skills": [], "full_skills": [], "scale": 1 },
        "mobile":   { "score": 0, "skills": [], "full_skills": [], "scale": 1 },
        "blockchain":   { "score": 0, "skills": [], "full_skills": [], "scale": 1.6 }
    }
    # Generate skill section
    skill_groups = get_required_skill_groups(jd, position)
    skill_full_list = [ item["skillName"] for sub_list in skill_groups for item in sub_list ]

    for required_skill in required_skills:
        closest_category = { "score": 0, "category": "" }
        for category in skill_category_info:
            score = get_skill_relation_value(required_skill["skill"], category, nodes, 0.1)
            # skill_category_info[category]["score"] += score * skill_category_info[category]["scale"]
            if closest_category["score"] < score:
                closest_category = { "score": score, "category": category }
        category = closest_category["category"]
        skill_category_info[category]["skills"].append(required_skill["skill"])
        skill_category_info[category]["full_skills"].extend([ skill_name for skill_name in skill_full_list if skill_name == required_skill["skill"] ])

    del skill_category_info["dev"]
    for category in skill_category_info:
        score = 0
        if len(skill_category_info[category]["full_skills"]) > 0:
            score = similarity_nm(skill_full_list, skill_category_info[category]["full_skills"]) ** 2
        skill_category_info[category]["score"] = (score ** 1.8) * skill_category_info[category]["scale"]
        print(category, score)
    skill_categories = [ (skill_category_info[item]["score"], item) for item in skill_category_info ]

    current_category_progress = [0] * 6
    total_sentence_count = len(list(filter(lambda x: "exchangable" in x and x["exchangable"] is True, sentences)))
    total_category_score = sum([ cat[0] for cat in skill_categories ])
    
    skill_category_words = [ list(map(normalize_skill_name, skill_category_info[category[1]]["full_skills"])) * 2 for category in skill_categories ]
    selected_categories = []
    for (sentence_index, sentence) in enumerate(sentences):

        # Selecte exchangable slots
        if "exchangable" not in sentence or sentence["exchangable"] is False:
            continue
        limit_year = LIMIT_YEARS[sentence_index]

        # Determine in which category should select the sentence
        current_category_index = 0
        max_remain = 0
        while True:
            for index, category in enumerate(skill_categories):

                # Get last sequent sentence count for the same category
                # For decremental calculation
                sequent_count = 0
                selected_categories_len = len(selected_categories)
                for last in range(selected_categories_len):
                    if selected_categories[selected_categories_len - last - 1] != index:
                        break
                    sequent_count += 1
                
                # Get progress of the current category
                progress = current_category_progress[index] / total_sentence_count * total_category_score
                remain = (category[0] - progress) * (0.9 ** sequent_count)
                if max_remain < remain:
                    current_category_index = index
                    max_remain = remain
            if max_remain > 0:
                break
            current_category_progress = [0] * 6
            
        if len(skill_category_words[current_category_index]) == 0:
            current_category_name = skill_categories[current_category_index][1]
            skill_category_words[current_category_index] = list(map(normalize_skill_name, skill_category_info[current_category_name]["full_skills"])) * 2

        current_category_progress[current_category_index] += 1
        selected_categories.append(current_category_index)

        for index, category in enumerate(skill_categories):
            progress = current_category_progress[index] / total_sentence_count * total_category_score
            print(category[1], progress)
        print("")
        
        best_candidate_sentence = {
            "similarity": 0,
            "index": 0
        }
        for index, sentence_template in enumerate(sentence_db):
            if sentence_usage[index] is True:
                continue
            new_sentence_quality = sentence_template["quality"]
            new_sentences = generate_sentences_from_template(sentence_template)
            for new_sentence in new_sentences:
                relations = new_sentence["relations"]
                for relation in relations:
                    if relation not in nodes:
                        continue
                    if nodes[relation].data["release"] > limit_year:
                        break
                else:
                    vector_similarity = similarity_nm(skill_category_words[current_category_index], relations) ** 2
                    similarity = vector_similarity * new_sentence_quality
                    if best_candidate_sentence["similarity"] < similarity:
                        best_candidate_sentence = {
                            "similarity": similarity,
                            "vector_similarity": float(vector_similarity),
                            "sentence_quality": new_sentence_quality,
                            "among": skill_category_words[current_category_index][:],
                            "relations": relations,
                            "content": new_sentence["content"],
                            "index": index
                        }

        best_sentence_index = best_candidate_sentence["index"]
        sentence_usage[best_sentence_index] = True

        for relation in best_candidate_sentence["relations"]:
            if relation in skill_category_words[current_category_index]:
                skill_category_words[current_category_index].remove(relation)
        final_sentences[sentence_index] = {
            "content": best_candidate_sentence["content"],
            "metadata": best_candidate_sentence
        }
    
    return final_sentences

def generate_resume_sentences(position: str, required_skills, jd: str) -> list:
    sentences = generate_detailed_resume_sentences(position, required_skills, jd)
    return [ sentence["content"] for sentence in sentences ]