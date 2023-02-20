from .utils import get_most_relevant_template
from ._template import get_template_data

def generate_meta_data(position: str, required_skills):
    template_type = get_most_relevant_template(position, required_skills)
    try:
        template = get_template_data(template_type)
    except:
        return None
    
    # Initialze variables
    headline = template["headline"]
    summary = template["summary"]
    positions = template["positions"]
    return headline, summary, positions
