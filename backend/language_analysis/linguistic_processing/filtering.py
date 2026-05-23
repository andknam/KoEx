import os

from konlpy.tag import Komoran

from backend.gpt.spacing_normalizer import normalize_korean_spacing
from backend.language_analysis.linguistic_processing.grouping import group_komoran_tokens
from backend.language_analysis.linguistic_processing.preprocessing import (
    preprocess_text,
    replace_sajaseongeo_with_placeholders,
)
from backend.language_analysis.linguistic_processing.rule_matcher import (
    merge_aux_grammar_chunks,
)

EXCLUDE_TOKENS = {
    # Particles
    '은', '는', '이', '가', '를', '을', '에', '에서', '로', '으로',
    '과', '와', '도', '만', '까지', '밖에', '처럼', '보다', '든지',

    # Filler nouns / deictics
    '그', '저', '이', '것', '거', '게', '곳', '데', '때',

    # High-frequency verbs/adjectives (semantically empty)
    '있', '없', '하다', '되', '같다', '좋다', '많다', '싶다',

    # Generic nouns
    '말', '생각', '시간', '사람', '일', '경우', '정도', '문제', '자신',

    # Light adverbs / discourse fillers
    '좀', '또', '다시', '그래서', '그런데', '그러나', '왜냐하면', '하지만',

    # WH-words (who, what, where, etc) / vague targets
    '어떻게', '왜', '언제', '어디서', '누가', '무슨',
}

ALLOWED_POS = {
    "NNG",
    "NNP",
    "NNB",
    "NR",
    "VV",
    "VA",
    "VX",
    "VCN",
    "VCP",
    "MAG",
    "MAJ",
    "XR",
    "SN",
    "SL",
    "SH",
    "MM",
}

current_dir = os.path.dirname(__file__)
user_dic_path = os.path.join(current_dir, "user.dic")
komoran = Komoran(userdic=user_dic_path)


def filter_korean_tokens(text: str) -> list[tuple[str, str]]:
    """Run the full Korean token filtering pipeline."""
    text_with_placeholders, placeholder_map = prepare_text_for_tokenization(text)
    tagged_text = tokenize_text(text_with_placeholders)
    grouped_tokens = apply_grouping_pipeline(tagged_text)
    return filter_allowed_tokens(grouped_tokens, placeholder_map)


def prepare_text_for_tokenization(text: str) -> tuple[str, dict[str, str]]:
    preprocessed_text = preprocess_text(text)
    spaced_text = normalize_korean_spacing(preprocessed_text)
    return replace_sajaseongeo_with_placeholders(spaced_text)


def tokenize_text(text: str) -> list[tuple[str, str]]:
    tagged_text = komoran.pos(text)
    print(f"{tagged_text=}")
    return tagged_text


def apply_grouping_pipeline(
    tagged_tokens: list[tuple[str, str]]
) -> list[tuple[str, str]]:
    """Apply structural token grouping before final filtering."""
    merged_tokens = merge_aux_grammar_chunks(tagged_tokens)
    print(f"merged_chunks={merged_tokens}")

    grouped_tokens = group_komoran_tokens(merged_tokens)
    print(f"{grouped_tokens=}")
    return grouped_tokens


def is_allowed_content_token(token: str, tag: str) -> bool:
    return (
        tag in ALLOWED_POS or tag.startswith("aux_") or tag.startswith("verb_")
    ) and token not in EXCLUDE_TOKENS


def filter_allowed_tokens(
    grouped_tokens: list[tuple[str, str]], placeholder_map: dict[str, str]
) -> list[tuple[str, str]]:
    """
    Filters morphemes to include only meaningful content tokens,
    while restoring any placeholder-replaced 사자성어.
    """
    final_tokens: list[tuple[str, str]] = []

    for token, tag in grouped_tokens:
        if token in placeholder_map:
            final_tokens.append((placeholder_map[token], "NNP"))
            continue

        if token.startswith("＠＠"):
            continue

        if is_allowed_content_token(token, tag):
            final_tokens.append((token, tag))

    return final_tokens
