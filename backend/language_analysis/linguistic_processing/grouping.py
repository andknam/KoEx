PARTICLE_TAGS = {"JKS", "JKC", "JKO", "JKB", "JKG", "JX", "JC"}

def is_verb_like(tag: str) -> bool:
    return tag in {"VV", "VA", "VX", "VCN", "VCP"} or tag.startswith("verb_")

def group_komoran_tokens(tagged: list[tuple[str, str]]) -> list[tuple[str, str]]:
    grouped = []
    i = 0
    while i < len(tagged):
        word, tag = tagged[i]

        # keep pre-merged aux grammar tokens
        if tag.startswith(("aux_", "verb_")):
            if grouped:
                prev_word, prev_tag = grouped[-1]

                # merge with previous verb or treat as main verb
                if is_verb_like(prev_tag):
                    merged = prev_word + word
                    grouped[-1] = (merged, "VV")
                    i += 1
                    continue

            # treat standalone aux/verb chunks as main verb
            grouped.append((word, "VV"))
            i += 1
            continue

        # skip standalone particles (they shouldn't trigger group rules)
        if tag in PARTICLE_TAGS:
            i += 1
            continue

        # greedy aux/verb suffix merging (VX + ETM + NNB + JX + VV + ...)
        if is_verb_like(tag):
            base = word
            i += 1

            while i < len(tagged) and tagged[i][1] in {"ETM", "NNB", "JX", "VV", "EF", "EC"}:
                base += tagged[i][0]
                i += 1

            grouped.append((base, "VV"))
            continue

        # NNG + XSV + EF (e.g., 변화하다)
        # noun + verb-forming suffix + ending --> verb derived from noun
        if (
            tag == "NNG"
            and i + 2 < len(tagged)
            and tagged[i + 1][1] == "XSV"
            and tagged[i + 2][1] == "EF"
        ):
            grouped.append((word, "NNG"))  # base noun
            grouped.append((word + tagged[i + 1][0] + tagged[i + 2][0], "VV"))
            i += 3
            continue

        # NNG + XSV (+ EC) (e.g., 실천하고)
        # compound verb stem (with optional connector after)
        if tag == "NNG" and i + 1 < len(tagged):
            next_word, next_tag = tagged[i + 1]
            if next_tag == "XSV":
                if i + 2 < len(tagged) and tagged[i + 2][1].startswith("aux_"):
                    grouped.append((word, "NNG"))
                    grouped.append((word + next_word + tagged[i + 2][0], "VV"))
                    i += 3
                    continue

                grouped.append((word, "NNG"))
                combined = word + next_word
                i += 2

                if i < len(tagged) and tagged[i][1] in {"EC", "EF"}:
                    combined += tagged[i][0]
                    i += 1

                grouped.append((combined, "VV"))
                continue

        # VV + ETM (e.g., 하 + ㄹ → 할)
        if tag == "VV" and i + 1 < len(tagged):
            next_word, next_tag = tagged[i + 1]
            if next_tag == "ETM":
                combined = contract_korean([word, next_word])
                grouped.append((combined, "VV"))
                i += 2
                continue

        # NNG + XSA + EF (e.g., 평화롭다)
        # noun + adj-forming suffix + ending --> adj derived from noun
        if (
            tag == "NNG"
            and i + 2 < len(tagged)
            and tagged[i + 1][1] == "XSA"
            and tagged[i + 2][1] == "EF"
        ):
            grouped.append((word, "NNG"))  # base noun
            grouped.append((word + tagged[i + 1][0] + tagged[i + 2][0], "VA"))
            i += 3
            continue

        # NNG + XSN (e.g., 가능성)
        # noun + noun suffix = compound abstract noun
        if tag == "NNG" and i + 1 < len(tagged):
            next_word, next_tag = tagged[i + 1]
            if next_tag == "XSN":
                grouped.append((word, "NNG"))  # base noun
                grouped.append((word + next_word, "NNG"))
                i += 2
                continue

        # VV/VX/VA/VCN/VCP + EC/EF (e.g., 하고)
        # verb/adj stems + verb ending
        if is_verb_like(tag) and i + 1 < len(tagged):
            next_word, next_tag = tagged[i + 1]
            if next_tag in {"EC", "EF"}:
                grouped.append((word + next_word, tag))
                i += 2
                continue

        # Default case
        grouped.append((word, tag))
        i += 1

    # normalize: turn aux_*/verb_* tags into VV for downstream logic
    for idx, (word, tag) in enumerate(grouped):
        if tag.startswith(("aux_", "verb_")):
            grouped[idx] = (word, "VV")

    return grouped


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
