def extract_candidate_korean_words(filtered_tokens: list[tuple[str, str]]) -> list[str]:
    content_tags = {"NNG", "NNP", "VV", "VA", "VCN", "VX"}
    seen = set()
    base_words = []

    for word, tag in filtered_tokens:
        if tag in content_tags and word not in seen:
            base_words.append(word)
            seen.add(word)

    return base_words


def tag_if_derived_by_substring(entries: list[str]) -> list[dict]:
    """
    Takes a list of Korean word strings.
    Tags each as 'derived' if it starts with a previously seen word.
    Returns list of dicts with 'korean', 'is_derived', and optional 'base_form'.
    """
    seen = set()
    result = []

    for word in sorted(entries, key=len):
        base_form = None

        for existing in seen:
            if word.startswith(existing):
                base_form = existing
                break

        entry = {
            "korean": word,
            "is_derived": base_form is not None
        }
        if base_form:
            entry["base_form"] = base_form

        result.append(entry)

        if not base_form:
            seen.add(word)

    return result