from topic_modelling_keywords import get_keywords
import re

def filter_text(text):
    keywords = get_keywords()
    text = re.sub("[^a-zA-Z]", " ", text).lower().split()
    if len(set(keywords).intersection(set(text))) > 0:
        label = 1
    else:
        label = 0
    return label