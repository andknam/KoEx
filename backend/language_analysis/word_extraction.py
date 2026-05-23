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
    Tags each as 'derived' if it starts with a shorter base word.
    Returns entries in their original sentence order.
    """
    base_form_by_word: dict[str, str] = {}
    base_forms: list[str] = []

    for word in sorted(entries, key=len):
        for base_form in base_forms:
            if word.startswith(base_form):
                base_form_by_word[word] = base_form
                break
        else:
            base_forms.append(word)

    tagged_entries = []

    for word in entries:
        entry = {
            "korean": word,
            "is_derived": word in base_form_by_word,
        }

        if word in base_form_by_word:
            entry["base_form"] = base_form_by_word[word]

        tagged_entries.append(entry)

    return tagged_entries
