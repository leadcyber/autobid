from .config import MODEL_SAVE_PATH, FITLEVEL_POSITION_PATH
from .utils import predetermine_jd_fitness, get_required_skill_index_sequence, get_embedding_skill_list, get_title_score
import json

skill_name_list = get_embedding_skill_list()

def is_proper_position(title: str):
    fit_level_file = open(FITLEVEL_POSITION_PATH)
    fit_level = json.load(fit_level_file)
    fit_level_file.close()
    return get_title_score(title, fit_level) >= fit_level["level"]

def is_proper_jd(detail):
    global skill_name_list
    return True
    

def get_jd_rate(jd):
    global skill_name_list
    return 0
    # index_sequence = get_required_skill_index_sequence(detail, skill_name_list)
    # predicted = model.predict(np.array([index_sequence]))[0]
    # return predicted.tolist()