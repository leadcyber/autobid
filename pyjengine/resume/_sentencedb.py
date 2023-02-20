import time
import yaml
from .config import RESUME_TEMPLATE_PATH, SENTENCE_DB_CACHE_TTL

sentence_db = None
last_load_time = 0

def get_sentence_db():
    global last_load_time, sentence_db

    current_timestamp = time.time()
    if sentence_db is None or current_timestamp - last_load_time > SENTENCE_DB_CACHE_TTL:
        with open(f'{RESUME_TEMPLATE_PATH}/addition_data.yaml', "r") as stream:
            sentence_db = yaml.safe_load(stream)
        last_load_time = current_timestamp
    return sentence_db