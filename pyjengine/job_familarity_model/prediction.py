import numpy as np
import keras
from .config import MODEL_SAVE_PATH, FITLEVEL_POSITION_PATH
from .utils import predetermine_jd_fitness, get_required_skill_index_sequence, get_embedding_skill_list, get_title_score
import json

model = keras.models.load_model(MODEL_SAVE_PATH)
model.summary()

skill_name_list = get_embedding_skill_list()

def is_proper_position(title: str):
    fit_level_file = open(FITLEVEL_POSITION_PATH)
    fit_level = json.load(fit_level_file)
    fit_level_file.close()
    return get_title_score(title, fit_level) >= fit_level["level"]

def is_proper_jd(detail):
    global skill_name_list
    fit = predetermine_jd_fitness(detail)
    index_sequence = get_required_skill_index_sequence(detail, skill_name_list)
    if fit is None:
        predicted = model.predict(np.array([index_sequence]))[0]
        print(predicted)
        return predicted[0] < predicted[1]
    else:
        return fit

def get_jd_rate(detail):
    global skill_name_list
    index_sequence = get_required_skill_index_sequence(detail, skill_name_list)
    predicted = model.predict(np.array([index_sequence]))[0]
    return predicted.tolist()