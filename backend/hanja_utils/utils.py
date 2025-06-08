import re
import os
from konlpy.tag import Okt, Komoran
from backend.gpt.hanja_batcher import generate_hanja_for_words

okt = Okt()

current_dir = os.path.dirname(__file__)
user_dic_path = os.path.join(current_dir, "user.dic")
komoran = Komoran(userdic=user_dic_path)

# Define 사자성어 list
sajaseongeo_list = ["유유자적", "고진감래", "전화위복", "각골난망"]

def strip_suffixes(text: str) -> str:
    # Simple rule: remove '한' when it comes directly after 사자성어
    for phrase in sajaseongeo_list:
        text = text.replace(phrase + "한", phrase)
    return text

def generate_placeholder(idx: int) -> str:
    return f"＠＠{idx}"  # Full-width @ (U+FF20)

def filter_korean_tokens(text: str) -> list[str]:
    # Strip suffixes from 사자성어
    text = strip_suffixes(text)

    # Remove non-Hangul except space
    text = re.sub(r"[^\uac00-\ud7a3\s]", "", text)

    # Detect 사자성어 with Komoran
    komoran_tagged = komoran.pos(text)
    placeholder_map = {}

    for idx, (word, _) in enumerate(komoran_tagged):
        if word in sajaseongeo_list and word not in placeholder_map.values():
            placeholder = generate_placeholder(len(placeholder_map))
            text = text.replace(word, placeholder, 1)
            placeholder_map[placeholder] = word

    # Tokenize using Okt on placeholdered text
    okt_tagged = okt.pos(text, stem=True)
    allowed_pos = {
        'Noun', 'Adverb', 'Verb', 'Adjective',
        'Alpha', 'Number', 'Foreign', 'Determiner'
    }

    final_tokens = []
    for word, tag in okt_tagged:
        if word in placeholder_map:
            final_tokens.append(placeholder_map[word])
        elif tag in allowed_pos:
            final_tokens.append(word)

    return final_tokens

def korean_to_hanja(input: str) -> list:
    filtered_tokens = filter_korean_tokens(input)
    return generate_hanja_for_words(filtered_tokens)

# if __name__ == "__main__":
#     print(filter_korean_tokens("요즘은 마음과 몸을 편안하게 하며 유유자적한 일상을 보내고 있는 것 같아"))
