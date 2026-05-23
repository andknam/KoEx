CONTENT_TAGS = {"NNG", "NNP", "VV", "VA", "VCN", "VX", "XR"}


def extract_candidate_korean_words(filtered_tokens: list[tuple[str, str]]) -> list[str]:
    seen: set[str] = set()
    candidate_words: list[str] = []

    for word, tag in filtered_tokens:
        if tag not in CONTENT_TAGS or word in seen:
            continue

        candidate_words.append(word)
        seen.add(word)

    return candidate_words


def tag_if_derived_by_substring(entries: list[str]) -> list[dict]:
    """
    Takes a list of Korean word strings.
    Tags each as 'derived' if it starts with a previously seen word.
    Returns list of dicts with 'korean', 'is_derived', and optional 'base_form'.
    """
    base_forms: set[str] = set()
    tagged_entries = []

    for word in sorted(entries, key=len):
        base_form = None

        for existing in base_forms:
            if word.startswith(existing):
                base_form = existing
                break

        entry = {
            "korean": word,
            "is_derived": base_form is not None
        }
        if base_form:
            entry["base_form"] = base_form

        tagged_entries.append(entry)

        if not base_form:
            base_forms.add(word)

    return tagged_entries
