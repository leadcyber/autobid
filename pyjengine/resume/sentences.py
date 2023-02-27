from skill.utils import normalize_skill_name
from skill.skill_tree import get_skill_tree, get_skill_relation_value
from .utils import get_most_relevant_template
from ._template import get_template_data
from ._sentencedb import get_sentence_db
import math

def generate_detailed_resume_sentences(position: str, required_skills) -> str:
    (root, nodes) = get_skill_tree()
    template_type = get_most_relevant_template(position, required_skills)
    try:
        template = get_template_data(template_type)
    except:
        return None

    sentences = template["default_sentences"]
    final_sentences = []
    for sentence in sentences:
        final_sentences.append(sentence["content"])
    if len(required_skills) == 0:
        return final_sentences
    
    initial_satisfactions = template["initial_satisfaction"]
    template_efficiencies = []
    familarities = {}
    satisfactions = {}
    importances = {}
    sentence_impacts = {}
    levels = {}

    for required_skill in required_skills:
        norm_skill = normalize_skill_name(required_skill["skill"])
        familarities[norm_skill] = required_skill["familarity"]
        importances[norm_skill] = required_skill["importance"]
    for skill_name in nodes:
        level = nodes[skill_name].data["level"]
        levels[skill_name] = level

    skill_category_info = {
        "frontend": { "score": 0.03, "skills": [], "fullname": "Front-End Development", "scale": 1.5, "default": ["React"] },
        "backend":  { "score": 0.02, "skills": [], "fullname": "Back-End Development", "scale": 1, "default": ["Node"] },
        "dev":      { "score": 0.01, "skills": [], "fullname": "Development Management", "scale": 0.3, "default": ["Agile"] },
        "cloud":    { "score": 0, "skills": [], "fullname": "Cloud Development", "scale": 0.8, "default": ["AWS"] },
        "database": { "score": 0, "skills": [], "fullname": "DB Administration", "scale": 0.7, "default": ["MySQL"] },
        "mobile":   { "score": 0, "skills": [], "fullname": "Mobile Development", "scale": 0.7, "default": ["React Native"] },
        "blockchain":   { "score": 0, "skills": [], "fullname": "Blockchain Development", "scale": 0.7, "default": ["Web3"] }
    }
    # Generate skill section
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
    if len(filter(lambda x: x[0] > 0.1, skill_categories)) < 3:
        skill_categories = skill_categories[:3]
    
    # Calculate efficiency for every sentences and satisfaction value for every required skills
    for (index, sentence) in enumerate(sentences):
        content = sentence["content"]
        relations = sentence["relation"]
        sentence_impact = sentence["impact"]
        sentence_impacts[content] = sentence_impact
        exchangable = sentence["exchangable"]

        for relation in 

        skill_category_info[]

        efficiency = 0
        x = len(relations)
        focus_efficiency = 1 / (1 + math.exp(x * 2/3 - 4))
        for relation in relations:
            relation_efficiency = 0
            # debugger.println(f"\n--------------------- {relation} ---------------------\n")
            for required_skill in required_skills:
                relation_value = get_skill_relation_value(relation, normalize_skill_name(required_skill["skill"]), nodes)
                relation_efficiency = max(relation_efficiency, relation_value * required_skill["importance"] * focus_efficiency)
                # debugger.println(f"{relation}\t<->\t{required_skill['skill']}\t:{relation_value}")
                satisfactions[relation] = satisfactions.setdefault(relation, 0) + relation_value * sentence_impact * focus_efficiency
            efficiency += relation_efficiency
        template_efficiencies.append({"content": content, "efficiency": efficiency, "index": index})
    
    # Calculate score for every sentences
    score_values = []
    satisfaction_weight = 1
    familarity_weight = 0.5
    importance_weight = 0.5
    for skill_name in familarities:
        satisfaction = satisfactions[skill_name] if skill_name in satisfactions else 0
        familarity = familarities[skill_name]
        importance = importances[skill_name]
        score_values.append({
            "skill_name": skill_name,
            "score": importance * importance_weight + familarity * familarity_weight - satisfaction * satisfaction_weight
        })
    score_values.sort(key=lambda x: x["score"], reverse=True)
    print("\n".join(map(lambda x: x["skill_name"] + " : " + str(x["score"]), score_values)))
    
    # Get missing skills
    max_skill_consideration = 5
    skills2replace = [ item["skill_name"] for item in score_values[:5] ]
    max_satisfactions = sorted([ satisfactions[skill] for skill in satisfactions ], reverse=True)[:max_skill_consideration]
    skills2replace = list(filter(lambda x: x not in satisfactions or satisfactions[x] not in max_satisfactions, skills2replace))
    # print("skills2replace", skills2replace)

    if len(skills2replace) > 0:
        # Get score for additional sentences
        additional_sentences = get_sentence_db()
        additional_efficiencies = []
        available_sentences = []
        for sentence in additional_sentences:
            relations = sentence["relation"]
            content = sentence["content"]
            sentence_quality = sentence["quality"]

            efficiencies = []
            x = len(relations)
            focus_efficiency = 1 / (1 + math.exp(x * 2/3 - 4))
            for (index, skill2replace) in enumerate(skills2replace):
                relation_efficiency = 0
                for relation in relations:
                    relation_value = get_skill_relation_value(relation, skill2replace, nodes)
                    relation_efficiency = max(relation_efficiency, relation_value * importances[skill2replace] * focus_efficiency)
                relation_efficiency *= sentence_quality
                relation_efficiency *= focus_efficiency
                if relation_efficiency > 0:
                    efficiencies.append([index, relation_efficiency])
            if len(efficiencies) > 0:
                additional_efficiencies.append(efficiencies)
                available_sentences.append(content)
        
        # Get sentences to be replaced
        max_replacement = 6
        count2replace = min(max_replacement, len(available_sentences))
        inefficient_sentences = sorted(template_efficiencies, key=lambda x: x["efficiency"] / sentence_impacts[x["content"]])[0:count2replace]

        # Get selected sentences to replace
        used = [False] * count2replace
        addition_score = [0] * len(skills2replace)
        selected_used = []
        min_max_score = -1
        sum_max_score = -1
        def _get_max_match(current_count, current_index):
            nonlocal min_max_score, selected_used, used, additional_efficiencies, addition_score, sum_max_score
            if current_count == count2replace:
                min_addition_score = min(addition_score)
                sum_addition_score = sum(addition_score)
                if min_addition_score > min_max_score or (min_addition_score == min_max_score and sum_addition_score > sum_max_score):
                    selected_used = used.copy()
                    min_max_score = min_addition_score
                    sum_max_score = sum_addition_score
                return
            used[current_index] = True
            for eff in additional_efficiencies[current_index]:
                addition_score[eff[0]] += eff[1]
            _get_max_match(current_count + 1, current_index + 1)
            used[current_index] = False
            for eff in additional_efficiencies[current_index]:
                addition_score[eff[0]] -= eff[1]
            _get_max_match(current_count + 1, current_index)
        _get_max_match(0, 0)

        # Sort selected sentences for more impact
        selected_sentences = []
        for (index, is_used) in enumerate(selected_used):
            if is_used:
                selected_sentences.append(index)
        used = [False] * count2replace

        def _get_sentence_order_key(selected_index):
            score = 0
            for eff in additional_efficiencies[selected_index]:
                score += importances[skills2replace[eff[0]]] * eff[1]
            return score
        ordered_sentences = [ available_sentences[index] for index in sorted(selected_sentences, key=_get_sentence_order_key) ]

        # Replace sentences
        for (index, inefficient_sentence) in enumerate(inefficient_sentences):
            if inefficient_sentence["index"] < 12:
                final_sentences[inefficient_sentence["index"]] = ordered_sentences[index]
    return final_sentences

def generate_resume_sentences(position: str, required_skills) -> str:
    sentences = generate_detailed_resume_sentences(position, required_skills)
    return sentences