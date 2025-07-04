import os

from konlpy.tag import Komoran

from backend.language_analysis.linguistic_processing.preprocessing import preprocess_text, replace_sajaseongeo_with_placeholders
from backend.language_analysis.linguistic_processing.rule_matcher import merge_aux_grammar_chunks
from backend.language_analysis.linguistic_processing.grouping import group_komoran_tokens

EXCLUDE_TOKENS = {
    # Particles
    '은', '는', '이', '가', '를', '을', '에', '에서', '로', '으로',
    '과', '와', '도', '만', '까지', '밖에', '처럼', '보다', '든지',

    # Filler nouns / deictics
    '그', '저', '이', '것', '거', '곳', '데', '때',

    # High-frequency verbs/adjectives (semantically empty)
    '있', '없', '하다', '되', '같다', '좋다', '많다', '싶다',

    # Generic nouns
    '말', '생각', '시간', '사람', '일', '경우', '정도', '문제', '자신',

    # Light adverbs / discourse fillers
    '좀', '또', '다시', '그래서', '그런데', '그러나', '왜냐하면', '하지만',

    # WH-words (who, what, where, etc) / vague targets
    '어떻게', '왜', '언제', '어디서', '누가', '무슨',
}

current_dir = os.path.dirname(__file__)
user_dic_path = os.path.join(current_dir, "user.dic")
komoran = Komoran(userdic=user_dic_path)


def filter_korean_tokens(text: str) -> list[tuple[str, str]]:
    # preprocess text + replace idioms with placeholders
    preprocessed_text = preprocess_text(text)
    text_w_placeholder, placeholder_map = replace_sajaseongeo_with_placeholders(preprocessed_text)

    # tokenize the input
    tagged_text = komoran.pos(text_w_placeholder)
    print(f"{tagged_text=}")

    return filter_allowed_tokens(tagged_text, placeholder_map)

def filter_allowed_tokens(tagged: list[tuple[str, str]], placeholder_map: dict) -> list[tuple[str, str]]:
    """
    Filters morphemes to include only meaningful content tokens,
    while restoring any placeholder-replaced 사자성어.
    """
    ALLOWED_POS = {
        'NNG', 'NNP', 'NNB', 'NR',      # Nouns
        'VV', 'VA', 'VX', 'VCN', 'VCP', # Verbs, adjectives, auxiliary, copula
        'MAG', 'MAJ',                   # Adverbs
        'XR',                           # Roots
        'SN', 'SL', 'SH',               # Numbers, foreign, sino
        'MM'                            # Determiner
    }

    # merge auxiliary and grammar phrases like 하겠다, 나가야 하다, etc.
    grouped = merge_aux_grammar_chunks(tagged)
    print(f"merged_chunks={grouped}")

    # group morphologically relevant constructions (e.g., NNG + XSV + EF → 변화하다)
    grouped = group_komoran_tokens(grouped)
    print(f"{grouped=}")
    final_tokens = []

    for token, tag in grouped:
        if token in placeholder_map:
            final_tokens.append((placeholder_map[token], 'NNP'))

        elif token.startswith("＠＠"):
            continue

        elif (tag in ALLOWED_POS or tag.startswith("aux_") or tag.startswith("verb_")):
            if token not in EXCLUDE_TOKENS:
                final_tokens.append((token, tag))

    return final_tokens
