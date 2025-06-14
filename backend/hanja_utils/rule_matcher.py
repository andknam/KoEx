import yaml
from typing import List, Tuple

with open("backend/hanja_utils/auxiliary_grammar_rules.yaml", encoding="utf-8") as f:
    GRAMMAR_RULES = yaml.safe_load(f)

def match_rule(tagged, i, rule):
    pattern = rule["pattern"]
    if i + len(pattern) > len(tagged):
        return None

    matched_tokens = []
    for offset, cond in enumerate(pattern):
        token, tag = tagged[i + offset]
        if "tag" in cond and cond["tag"] != tag:
            return None

        if "token" in cond and cond["token"] != token:
            return None

        matched_tokens.append(token)

    combined = "".join(matched_tokens)

    # 아야하겠다 / 어야하겠다 → 야겠다
    if combined.endswith("아야하겠다") or combined.endswith("어야하겠다"):
        combined = combined.replace("아야하겠다", "야겠다").replace("어야하겠다", "야겠다")

    # '하' + 'ㄹ' → '할'
    if combined.startswith('하ㄹ'):
        combined = combined.replace('하ㄹ', '할', 1)

    return "".join(combined)

def merge_aux_grammar_chunks(tagged: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """
    Merge morpheme sequences based on loaded grammar rules.
    Returns a new list of (token, tag) pairs with merged grammar chunks.
    """
    merged = []
    i = 0
    while i < len(tagged):
        matched = None

        print(f"\nChecking at position {i}: {tagged[i:i+5]}")

        for rule in GRAMMAR_RULES:
            result = match_rule(tagged, i, rule)
            if result:
                print(f"→ Matched rule: {rule['name']} → {result}")
                merged.append((result, 'VV'))  # treat as verb phrase
                i += len(rule["pattern"])
                break
        else:
            merged.append(tagged[i])
            i += 1

    return merged