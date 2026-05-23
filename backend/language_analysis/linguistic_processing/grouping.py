from collections.abc import Callable


PARTICLE_TAGS = {"JKS", "JKC", "JKO", "JKB", "JKG", "JX", "JC"}
VERB_LIKE_TAGS = {"VV", "VA", "VX", "VCN", "VCP"}
VERB_CHAIN_SUFFIX_TAGS = {"ETM", "NNB", "JX", "VV", "EF", "EC"}
ENDING_TAGS = {"EC", "EF"}

GroupedToken = tuple[str, str]
MatchResult = tuple[list[GroupedToken], int] | None
GroupingRule = Callable[[list[GroupedToken], int], MatchResult]


def group_komoran_tokens(tagged: list[tuple[str, str]]) -> list[tuple[str, str]]:
    grouped: list[tuple[str, str]] = []
    i = 0

    while i < len(tagged):
        grouped, i = apply_grouping_rules(grouped, tagged, i)

    return normalize_grouped_tags(grouped)


def apply_grouping_rules(
    grouped: list[tuple[str, str]], tagged: list[tuple[str, str]], index: int
) -> tuple[list[tuple[str, str]], int]:
    word, tag = tagged[index]

    if tag.startswith(("aux_", "verb_")):
        return merge_premerged_verb_chunk(grouped, tagged, index)

    if tag in PARTICLE_TAGS:
        return grouped, index + 1

    for matcher in GROUPING_RULES:
        match = matcher(tagged, index)
        if not match:
            continue

        grouped.extend(match[0])
        return grouped, match[1]

    grouped.append((word, tag))
    return grouped, index + 1


def normalize_grouped_tags(
    grouped: list[tuple[str, str]]
) -> list[tuple[str, str]]:
    normalized: list[tuple[str, str]] = []

    for word, tag in grouped:
        if tag.startswith(("aux_", "verb_")):
            normalized.append((word, "VV"))
        else:
            normalized.append((word, tag))

    return normalized


def is_verb_like(tag: str) -> bool:
    return tag in VERB_LIKE_TAGS or tag.startswith("verb_")


def merge_premerged_verb_chunk(
    grouped: list[tuple[str, str]], tagged: list[tuple[str, str]], index: int
) -> tuple[list[tuple[str, str]], int]:
    word, _ = tagged[index]

    if grouped and is_verb_like(grouped[-1][1]):
        prev_word, _ = grouped[-1]
        grouped[-1] = (prev_word + word, "VV")
        return grouped, index + 1

    grouped.append((word, "VV"))
    return grouped, index + 1


def match_verb_chain(
    tagged: list[tuple[str, str]], index: int
) -> MatchResult:
    word, tag = tagged[index]
    if not is_verb_like(tag):
        return None

    combined = word
    next_index = index + 1

    while next_index < len(tagged) and tagged[next_index][1] in VERB_CHAIN_SUFFIX_TAGS:
        combined += tagged[next_index][0]
        next_index += 1

    return [(combined, "VV")], next_index


def match_noun_derived_form(
    tagged: list[tuple[str, str]], index: int
) -> MatchResult:
    word, tag = tagged[index]
    if tag != "NNG" or index + 1 >= len(tagged):
        return None

    next_word, next_tag = tagged[index + 1]

    if next_tag == "XSV":
        return build_noun_verb_group(tagged, index, word, next_word)

    if (
        next_tag == "XSA"
        and index + 2 < len(tagged)
        and tagged[index + 2][1] == "EF"
    ):
        adjective = word + next_word + tagged[index + 2][0]
        return [(word, "NNG"), (adjective, "VA")], index + 3

    if next_tag == "XSN":
        return [(word, "NNG"), (word + next_word, "NNG")], index + 2

    return None


def match_contracted_verb_form(
    tagged: list[tuple[str, str]], index: int
) -> MatchResult:
    word, tag = tagged[index]

    if (
        tag == "VV"
        and index + 1 < len(tagged)
        and tagged[index + 1][1] == "ETM"
    ):
        combined = contract_korean([word, tagged[index + 1][0]])
        return [(combined, "VV")], index + 2

    if (
        is_verb_like(tag)
        and index + 1 < len(tagged)
        and tagged[index + 1][1] in ENDING_TAGS
    ):
        return [(word + tagged[index + 1][0], tag)], index + 2

    return None


GROUPING_RULES: tuple[GroupingRule, ...] = (
    match_verb_chain,
    match_noun_derived_form,
    match_contracted_verb_form,
)


def build_noun_verb_group(
    tagged: list[tuple[str, str]], index: int, noun: str, suffix: str
) -> tuple[list[tuple[str, str]], int]:
    if index + 2 < len(tagged) and tagged[index + 2][1] == "EF":
        verb = noun + suffix + tagged[index + 2][0]
        return [(noun, "NNG"), (verb, "VV")], index + 3

    if index + 2 < len(tagged) and tagged[index + 2][1].startswith("aux_"):
        verb = noun + suffix + tagged[index + 2][0]
        return [(noun, "NNG"), (verb, "VV")], index + 3

    combined = noun + suffix
    index += 2

    if index < len(tagged) and tagged[index][1] in ENDING_TAGS:
        combined += tagged[index][0]
        index += 1

    return [(noun, "NNG"), (combined, "VV")], index


def contract_korean(tokens: list[str]) -> str:
    """
    Applies basic Korean morphophonological contractions.
    For example:
    - 하 + 였 → 했
    - 하 + 았 → 했
    - 끝나 + 았 → 끝났
    - 하 + ㄹ → 할
    - 아야하겠다 / 어야하겠다 → 야겠다
    """

    if len(tokens) < 2:
        return "".join(tokens)

    # 하 + ㄹ → 할 (e.g., 하ㄹ 수 있다)
    if tokens[0] == "하" and tokens[1] == "ㄹ":
        tokens[0] = "할"
        del tokens[1]

    # special endings like 아야하겠다 / 어야하겠다 → 야겠다
    joined = "".join(tokens)
    if joined.endswith("아야하겠다") or joined.endswith("어야하겠다"):
        joined = joined.replace("아야하겠다", "야겠다").replace("어야하겠다", "야겠다")
        return joined

    # iterate through pairs to contract verb stems
    i = 0
    while i < len(tokens) - 1:
        prev, curr = tokens[i], tokens[i + 1]

        # 하 + 았/었/였 → 했
        if prev == "하" and curr in {"았", "었", "였"}:
            tokens[i] = "했"
            del tokens[i + 1]
            continue

        # 가 + 았 → 갔
        if prev.endswith("가") and curr == "았":
            tokens[i] = prev[:-1] + "갔"
            del tokens[i + 1]
            continue

        # 끝나 + 았 → 끝났
        if prev.endswith("나") and curr == "았":
            tokens[i] = prev[:-1] + "났"
            del tokens[i + 1]
            continue

        # 자 + 았 → 잤
        if prev.endswith("자") and curr == "았":
            tokens[i] = prev[:-1] + "잤"
            del tokens[i + 1]
            continue

        # 주 + 었 → 줬
        if prev.endswith("주") and curr == "었":
            tokens[i] = prev[:-1] + "줬"
            del tokens[i + 1]
            continue

        i += 1

    return "".join(tokens)
