from konlpy.tag import Komoran
import os
import re

from backend.hanja_utils.morph_utils import contract_korean

current_dir = os.path.dirname(__file__)
user_dic_path = os.path.join(current_dir, "user.dic")
komoran = Komoran(userdic=user_dic_path)

sajaseongeo_list = ["유유자적", "고진감래", "전화위복", "각골난망", "작심삼일"]

particle_tags = {'JKS', 'JKC', 'JKO', 'JKB', 'JKG', 'JX', 'JC'}

def strip_suffixes(text: str) -> str:
    # TODO: extend this to other suffixes
    # remove '한' when it comes directly after 사자성어
    for phrase in sajaseongeo_list:
        text = text.replace(phrase + "한", phrase)
    return text

# trick used to avoid collison with regular symbols
# not split up by tokenizers
def generate_placeholder(idx: int) -> str:
    return f"＠＠{idx}"  # Full-width @ (U+FF20)

def preprocess_text(text: str) -> str:
    """Strips 사자성어 suffixes and removes non-Hangul chars."""
    text = strip_suffixes(text)
    return re.sub(r"[^\uac00-\ud7a3\s]", "", text)


def replace_sajaseongeo_with_placeholders(text: str) -> tuple[str, dict]:
    """Replaces 사자성어 with placeholders using regex to handle particles."""
    placeholder_map = {}
    for _, phrase in enumerate(sajaseongeo_list):
        # Match phrase followed by end or Korean particle (e.g., 로, 은, 도, etc.)
        pattern = re.compile(rf"{re.escape(phrase)}(?=[\s\uac00-\ud7a3]{{0,1}}[은는이가을를에로과와도])?")
        if re.search(pattern, text):
            placeholder = generate_placeholder(len(placeholder_map))
            text = re.sub(pattern, placeholder, text, count=1)
            placeholder_map[placeholder] = phrase

    return text, placeholder_map

def group_komoran_tokens(tagged: list[tuple[str, str]]) -> list[tuple[str, str]]:
    grouped = []
    i = 0
    while i < len(tagged):
        word, tag = tagged[i]

        # Skip standalone particles (they shouldn't trigger group rules)
        if tag in particle_tags:
            i += 1
            continue

        # NNG + XSV + EF (e.g., 변화하다)
        # noun + verb-forming suffix + ending --> verb derived from noun
        if (
            tag == 'NNG'
            and i + 2 < len(tagged)
            and tagged[i + 1][1] == 'XSV'
            and tagged[i + 2][1] == 'EF'
        ):
            grouped.append((word, 'NNG'))  # base noun
            grouped.append((word + tagged[i + 1][0] + tagged[i + 2][0], 'VV'))
            i += 3
            continue

        # NNG + XSV (+ EC) (e.g., 실천하고)
        # compound verb stem (with optional connector after)
        if tag == 'NNG' and i + 1 < len(tagged):
            next_word, next_tag = tagged[i + 1]
            if next_tag == 'XSV':
                grouped.append((word, 'NNG'))  # base noun
                combined = word + next_word
                i += 2
                # Look ahead to optionally include EC/EF (e.g., 실천 + 하 + 고 → 실천하고)
                if i < len(tagged) and tagged[i][1] in {'EC', 'EF'}:
                    combined += tagged[i][0]
                    i += 1
                grouped.append((combined, 'VV'))
                continue

        # VV/VX/VA/VCN/VCP + EC/EF (e.g., 하고)
        # verb/adj stems + verb ending
        if tag in {'VV', 'VX', 'VA', 'VCN', 'VCP'} and i + 1 < len(tagged):
            next_word, next_tag = tagged[i + 1]
            if next_tag in {'EC', 'EF'}:
                grouped.append((word + next_word, tag))
                i += 2
                continue

        # VV + ETM (e.g., 하 + ㄹ → 할)
        if tag == 'VV' and i + 1 < len(tagged):
            next_word, next_tag = tagged[i + 1]
            if next_tag == 'ETM':
                combined = contract_korean([word, next_word])
                grouped.append((combined, 'VV'))
                i += 2
                continue

        # NNG + XSA + EF (e.g., 평화롭다)
        # noun + adj-forming suffix + ending --> adj derived from noun
        if (
            tag == 'NNG'
            and i + 2 < len(tagged)
            and tagged[i + 1][1] == 'XSA'
            and tagged[i + 2][1] == 'EF'
        ):
            grouped.append((word, 'NNG'))  # base noun
            grouped.append((word + tagged[i + 1][0] + tagged[i + 2][0], 'VA'))
            i += 3
            continue

        # NNG + XSN (e.g., 가능성)
        # noun + noun suffix = compound abstract noun
        if tag == 'NNG' and i + 1 < len(tagged):
            next_word, next_tag = tagged[i + 1]
            if next_tag == 'XSN':
                grouped.append((word, 'NNG'))  # base noun
                grouped.append((word + next_word, 'NNG'))
                i += 2
                continue

        # Default case
        grouped.append((word, tag))
        i += 1

    return grouped