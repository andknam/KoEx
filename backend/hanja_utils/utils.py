import re
import os

from hanja import translate
from konlpy.tag import Okt

from backend.gpt.hanja_batcher import generate_hanja_for_words

okt = Okt()

def load_substitution_dict():
    base_path = os.path.dirname(__import__('hanja').__file__)
    path = os.path.join(base_path, 'data', 'substitution.txt')

    substitution_dict = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            if '\t' in line:
                word, hanja = line.strip().split('\t')
                substitution_dict[word] = hanja
    return substitution_dict

def filter_korean_tokens(text):
    # Remove non-Hangul (excluding spaces)
    text = re.sub(r"[^\uac00-\ud7a3\s]", "", text)
    
    # Get part-of-speech tagged tokens
    tagged = okt.pos(text)

    # Keep only desired POS
    allowed_pos = {'Noun', 'Adverb', 'Verb'}
    filtered = [word for word, tag in tagged if tag in allowed_pos]
    
    return filtered

def korean_to_hanja(input: str) -> list:
    filtered_tokens = filter_korean_tokens(input)
    results = generate_hanja_for_words(filtered_tokens)

    return results