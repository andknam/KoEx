from typing import List, Tuple
from konlpy.tag import Komoran

from backend.hanja_utils.rule_matcher import merge_aux_grammar_chunks
from backend.hanja_utils.tokenizer import group_komoran_tokens

komoran = Komoran()

STOPWORDS = {
    '것', '수', '좀', '더', '이제', '그래서', '근데', '거', '그', '저', '좀', '거의', '정말', '그냥',
    '자신', '이런', '저런', '우리', '너무', '다시', '항상', '때문', '무엇', '모든', '아무', '다른'
}

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

    # Merge auxiliary and grammar phrases like 하겠다, 나가야 하다, etc.
    grouped = merge_aux_grammar_chunks(tagged)

    # Group morphologically relevant constructions (e.g., NNG + XSV + EF → 변화하다)
    grouped = group_komoran_tokens(grouped)
    final_tokens = []

    for token, tag in grouped:
        if token in placeholder_map:
            final_tokens.append((placeholder_map[token], 'NNP'))
        # dont re-tag placeholders
        elif token.startswith("＠＠"):
            continue
        elif tag in ALLOWED_POS and token not in STOPWORDS:
            final_tokens.append((token, tag))
        elif token not in STOPWORDS:
            tagged_token = komoran.pos(token)
            # nothing valid returned
            if not tagged_token:
                continue 
            for _, sub_tag in tagged_token:
                if sub_tag in ALLOWED_POS:
                    final_tokens.append((token, sub_tag))  # keep surface form, fix with new tag
                    break

    return final_tokens
