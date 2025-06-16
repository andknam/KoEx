import os
import re
from konlpy.tag import Okt, Komoran

from backend.gpt.hanja_batcher import generate_hanja_for_words
from backend.hanja_utils.tokenizer import (
    strip_suffixes,
    replace_sajaseongeo_with_placeholders,
)
from backend.hanja_utils.filters import filter_allowed_tokens

okt = Okt()
current_dir = os.path.dirname(__file__)
user_dic_path = os.path.join(current_dir, "user.dic")
komoran = Komoran(userdic=user_dic_path)


def preprocess_text(text: str) -> str:
    text = strip_suffixes(text)
    return re.sub(r"[^\uac00-\ud7a3\s]", "", text)


def filter_korean_tokens(text: str) -> list[tuple[str, str]]:
    preprocessed_text = preprocess_text(text)
    text_w_placeholder, placeholder_map = replace_sajaseongeo_with_placeholders(preprocessed_text)
    tagged_text = komoran.pos(text_w_placeholder)
    return filter_allowed_tokens(tagged_text, placeholder_map)


def korean_to_hanja(input_query: str) -> list[dict]:
    """
    Extracts meaningful Korean words from the input, filters them by part of speech,
    and returns enriched Hanja information using GPT.
    """
    filtered_tokens = filter_korean_tokens(input_query)

    # Only allow base content words (e.g., 실천, 계획), not long fused forms
    content_tags = {'NNG', 'NNP', 'VV', 'VA', 'VCN', 'VX'}
    seen = set()
    tokens_for_hanja = []

    for word, tag in filtered_tokens:
        if tag in content_tags and len(word) <= 4 and word not in seen:
            tokens_for_hanja.append(word)
            seen.add(word)

    return generate_hanja_for_words(tokens_for_hanja)


def tag_derived_forms(entries: list[dict]) -> list[dict]:
    """
    Adds 'is_derived': True to entries whose Korean form is a longer derived variant
    of a previously seen shorter word (e.g., '실천하고' if '실천' already exists).
    """
    seen = set()
    result = []

    for entry in sorted(entries, key=lambda x: len(x["korean"])):
        word = entry["korean"]
        is_derived = any(existing in word for existing in seen)
        entry["is_derived"] = is_derived
        result.append(entry)
        if not is_derived:
            seen.add(word)

    return result