import spacy

TRANINED_COMPANY_MODEL = './company_name_detection_model/Model'

def parse_company_name(sentence: str):
    nlp2 = spacy.load(TRANINED_COMPANY_MODEL)
    doc = nlp2(sentence)
    candidates = [ ent.text for ent in doc.ents ]
    try:
        candidates.remove("Our")
    except:
        pass
    return candidates