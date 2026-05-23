import os

import yaml

from backend.language_analysis.linguistic_processing.grouping import contract_korean

RULES_PATH = os.path.join(
    os.path.dirname(__file__),
    "auxiliary_grammar_rules.yaml",
)

with open(RULES_PATH, encoding="utf-8") as f:
    GRAMMAR_RULES = yaml.safe_load(f)

TAG_EQUIVALENTS = {
    "EF": {"EF", "EC"},
    "VA": {"VA", "VX"},
    "VV": {"VV", "VX", "VA"},
    "VX": {"VX", "VA"},
}


def merge_aux_grammar_chunks(tagged: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """
    Merge morpheme sequences based on loaded grammar rules.
    At each position, greedily apply the longest matching rule.
    Returns a new list of (token, tag) pairs with merged grammar chunks.
    """
    merged = []
    i = 0
    while i < len(tagged):
        best_match, best_len = find_best_rule_match(tagged, i)

        if best_match:
            merged.append(best_match)
            i += best_len
        else:
            merged.append(tagged[i])
            i += 1

    return merged


def find_best_rule_match(
    tagged: list[tuple[str, str]], start_index: int
) -> tuple[tuple[str, str] | None, int]:
    best_match = None
    best_len = 0

    for rule in GRAMMAR_RULES:
        result = match_rule(tagged, start_index, rule)
        if not result:
            continue

        rule_len = len(rule["pattern"])
        if rule_len > best_len:
            best_match = result
            best_len = rule_len

    return best_match, best_len


def tag_matches(expected: str, actual: str) -> bool:
    return actual in TAG_EQUIVALENTS.get(expected, {expected})


def match_rule(
    tagged: list[tuple[str, str]], i: int, rule: dict
) -> tuple[str, str] | None:
    pattern = rule["pattern"]
    if i + len(pattern) > len(tagged):
        return None

    matched_tokens = []
    for offset, cond in enumerate(pattern):
        token, tag = tagged[i + offset]

        if "tag" in cond and not tag_matches(cond["tag"], tag):
            return None

        if "token" in cond and cond["token"] != token:
            return None

        matched_tokens.append(token)

    combined = contract_korean(matched_tokens)

    # print(f"[✔] Matched rule: {rule['name']} → {combined}")
    return (combined, rule.get("group_as", "VV"))
