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

def preprocess_text(text: str) -> str:
    """Strips 사자성어 suffixes and removes non-Hangul chars."""
    text = strip_suffixes(text)
    return re.sub(r"[^\uac00-\ud7a3\s]", "", text)

def replace_sajaseongeo_with_placeholders(text: str) -> tuple[str, dict]:
    """Replaces 사자성어 with placeholders using Komoran tagging."""
    placeholder_map = {}
    tagged = komoran.pos(text)

    for word, _ in tagged:
        if word in sajaseongeo_list and word not in placeholder_map.values():
            placeholder = generate_placeholder(len(placeholder_map))
            text = text.replace(word, placeholder, 1)
            placeholder_map[placeholder] = word

    return text, placeholder_map

particle_tags = {'JKS', 'JKC', 'JKO', 'JKB', 'JKG', 'JX', 'JC'}

def group_komoran_tokens(tagged: list[tuple[str, str]]) -> list[str]:
    grouped = []
    i = 0
    while i < len(tagged):
        word, tag = tagged[i]

        # Skip standalone particles (they shouldn't trigger group rules)
        if tag in particle_tags:
            i += 1
            continue

        # VV/VX/VA/VCN/VCP + EC/EF
        if tag in {'VV', 'VX', 'VA', 'VCN', 'VCP'} and i + 1 < len(tagged):
            next_word, next_tag = tagged[i + 1]
            if next_tag in {'EC', 'EF'}:
                grouped.append(word + next_word)
                i += 2
                continue

        # NNG + XSN (e.g., 가능성)
        if tag == 'NNG' and i + 1 < len(tagged):
            next_word, next_tag = tagged[i + 1]
            if next_tag == 'XSN':
                grouped.append(word + next_word)
                i += 2
                continue

        # NNG + XSV + EF (e.g., 변화하다)
        if (
            tag == 'NNG'
            and i + 2 < len(tagged)
            and tagged[i + 1][1] == 'XSV'
            and tagged[i + 2][1] == 'EF'
        ):
            grouped.append(word + tagged[i + 1][0] + tagged[i + 2][0])
            i += 3
            continue

        # NNG + XSA + EF (e.g., 평화롭다)
        if (
            tag == 'NNG'
            and i + 2 < len(tagged)
            and tagged[i + 1][1] == 'XSA'
            and tagged[i + 2][1] == 'EF'
        ):
            grouped.append(word + tagged[i + 1][0] + tagged[i + 2][0])
            i += 3
            continue

        # Default case
        grouped.append(word)
        i += 1

    return grouped

def filter_allowed_tokens(tagged: list[tuple[str, str]], placeholder_map: dict) -> list[str]:
    """Filters by allowed POS and replaces placeholders."""
    allowed_pos = {
        'NNG', 'NNP', 'NNB', 'NR',      # Nouns
        'VV', 'VA', 'VX', 'VCN', 'VCP', # Verbs, adjectives, auxiliary, copula
        'MAG', 'MAJ',                   # Adverbs
        'XR',                           # Roots
        'SN', 'SL', 'SH',               # Numbers, foreign, sino
        'MM'                            # Determiner
    }

    grouped = group_komoran_tokens(tagged)
    final_tokens = []

    for token in grouped:
        if token in placeholder_map:
            final_tokens.append(placeholder_map[token])
        else:
            # Re-tag individual token to get its POS
            tagged_token = komoran.pos(token)
            if tagged_token and tagged_token[0][1] in allowed_pos:
                final_tokens.append(token)

    return final_tokens

def filter_korean_tokens(text: str) -> list[str]:
    text = preprocess_text(text)
    text, placeholder_map = replace_sajaseongeo_with_placeholders(text)
    tagged = komoran.pos(text)
    return filter_allowed_tokens(tagged, placeholder_map)

def korean_to_hanja(input: str) -> tuple[list, list]:
    filtered_tokens = filter_korean_tokens(input)
    return generate_hanja_for_words(filtered_tokens)

# if __name__ == "__main__":
#     print(filter_korean_tokens("요즘은 마음과 몸을 편안하게 하며 유유자적한 일상을 보내고 있는 것 같아"))
