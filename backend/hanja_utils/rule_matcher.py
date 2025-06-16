import yaml
from typing import List, Tuple

from backend.hanja_utils.morph_utils import contract_korean

with open("backend/hanja_utils/auxiliary_grammar_rules.yaml", encoding="utf-8") as f:
    GRAMMAR_RULES = yaml.safe_load(f)

def match_rule(tagged, i, rule):
    pattern = rule["pattern"]
    if i + len(pattern) > len(tagged):
        return None

    matched_tokens = []
    for offset, cond in enumerate(pattern):
        token, tag = tagged[i + offset]

        # Check tag if specified
        if "tag" in cond and cond["tag"] != tag:
            return None
        # Check token if specified
        if "token" in cond and cond["token"] != token:
            return None

        matched_tokens.append(token)

    combined = contract_korean(matched_tokens)

    print(f"[✔] Matched rule: {rule['name']} → {combined}")
    return (combined, rule.get("group_as", "VV"))


def merge_aux_grammar_chunks(tagged: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """
    Merge morpheme sequences based on loaded grammar rules.
    At each position, greedily apply the longest matching rule.
    Returns a new list of (token, tag) pairs with merged grammar chunks.
    """
    merged = []
    i = 0
    while i < len(tagged):
        best_match = None
        best_len = 0

        for rule in GRAMMAR_RULES:
            result = match_rule(tagged, i, rule)
            if result:
                rule_len = len(rule["pattern"])
                if rule_len > best_len:
                    best_match = result
                    best_len = rule_len

        if best_match:
            merged.append(best_match)
            i += best_len
        else:
            merged.append(tagged[i])
            i += 1

    return merged