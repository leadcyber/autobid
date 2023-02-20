import time
import yaml
from .config import RESUME_TEMPLATE_PATH, TEMPLATE_CACHE_TTL

template = {}

def get_template_data(template_type):
    global template

    current_timestamp = time.time()
    if template_type not in template or current_timestamp - template[template_type]["last_load_time"] > TEMPLATE_CACHE_TTL:
        with open(f'{RESUME_TEMPLATE_PATH}/{template_type}_data.yaml', "r") as stream:
            template[template_type] = {
                "data": yaml.safe_load(stream),
                "last_load_time": current_timestamp
            }
    return template[template_type]["data"]


def get_template_meta_data(template_type):
    template_data = get_template_data(template_type)
    return template_data["headline"], template_data["summary"], template_data["positions"]

def get_template_sentences(template_type):
    template_data = get_template_data(template_type)
    return template_data["default_sentences"]