# backend/hanja_utils/hanja_pipeline.py

import os
import re
import yaml
from konlpy.tag import Okt, Komoran

from backend.gpt.hanja_batcher import generate_hanja_for_words
from backend.hanja_utils.rule_matcher import merge_aux_grammar_chunks
from backend.hanja_utils.tokenizer import (
    strip_suffixes,
    replace_sajaseongeo_with_placeholders,
    group_komoran_tokens,
)

okt = Okt()

current_dir = os.path.dirname(__file__)
user_dic_path = os.path.join(current_dir, "user.dic")
komoran = Komoran(userdic=user_dic_path)

particle_tags = {'JKS', 'JKC', 'JKO', 'JKB', 'JKG', 'JX', 'JC'}

def preprocess_text(text: str) -> str:
    text = strip_suffixes(text)
    return re.sub(r"[^\uac00-\ud7a3\s]", "", text)

def filter_allowed_tokens(tagged: list[tuple[str, str]], placeholder_map: dict) -> list[str]:
    allowed_pos = {
        'NNG', 'NNP', 'NNB', 'NR',
        'VV', 'VA', 'VX', 'VCN', 'VCP',
        'MAG', 'MAJ', 'XR', 'SN', 'SL', 'SH', 'MM'
    }
    grouped = merge_aux_grammar_chunks(tagged)
    grouped = group_komoran_tokens(grouped)
    final_tokens = []

    for token, tag in grouped:
        if token in placeholder_map:
            final_tokens.append(placeholder_map[token])
        elif tag in allowed_pos:
            final_tokens.append(token)
        else:
            tagged_token = komoran.pos(token)
            if tagged_token and tagged_token[0][1] in allowed_pos:
                final_tokens.append(token)

    return final_tokens

def filter_korean_tokens(text: str) -> list[str]:
    preprocessed_text = preprocess_text(text)
    text_w_placeholder, placeholder_map = replace_sajaseongeo_with_placeholders(preprocessed_text)
    tagged_text = komoran.pos(text_w_placeholder)

    return filter_allowed_tokens(tagged_text, placeholder_map)

def korean_to_hanja(input_query: str) -> tuple[list, list]:
    filtered_tokens = filter_korean_tokens(input_query)

    return generate_hanja_for_words(filtered_tokens)

def test_merge(input_tokens: list[tuple[str, str]], expected: list[str]):
    result = merge_aux_grammar_chunks(input_tokens)
    result_tokens = [token for token, _ in result]
    assert result_tokens == expected, f"\nExpected: {expected}\nGot:      {result_tokens}"
    print(f"✅ Passed: {' + '.join([t[0] for t in input_tokens])} → {' + '.join(expected)}")

if __name__ == "__main__":
    print("Running grammar chunking tests...\n")

    test_merge([('하', 'VV'), ('겠', 'EP'), ('다', 'EF')], ['하겠다'])
    test_merge([('나가', 'VV'), ('아야', 'EC'), ('하', 'VX'), ('겠', 'EP'), ('다', 'EF')], ['나가야겠다'])
    test_merge([('가', 'VV'), ('려고', 'EC'), ('하', 'VV'), ('다', 'EF')], ['가려고하다'])
    test_merge([('먹', 'VV'), ('고', 'EC'), ('싶', 'VA'), ('다', 'EF')], ['먹고싶다'])
    test_merge([('하', 'VV'), ('ㄹ', 'ETM'), ('수', 'NNG'), ('있', 'VV'), ('다', 'EF')], ['할수있다'])
    test_merge([('하', 'VV'), ('지', 'EC'), ('않', 'VX'), ('다', 'EF')], ['하지않다'])
    test_merge([('하', 'VV'), ('고', 'EC'), ('있', 'VX'), ('다', 'EF')], ['하고있다'])
    test_merge([('먹', 'VV'), ('었', 'EP'), ('다', 'EF')], ['먹었다'])

    print("\n✅ All tests passed.")
