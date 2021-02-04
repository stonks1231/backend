import spacy
import numpy
import spacy
from spacy.attrs import ENT_IOB, ENT_TYPE

nlp = spacy.load("en_core_web_sm")


def extract_company(id=None, text=None):
    """
    This method returns named entities that are tagged as ORG and noun(s) and proper noun(s)
    :param id: Reddit id
    :param text: Text
    :return: two lists one for named entities, noun(s) and proper noun(s)
    """
    doc = nlp(text)

    orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    tokens = [ent.text for ent in doc if 'NN' in ent.tag_]
    return orgs, tokens

if __name__ == '__main__':
    extract_named_entities("test")
