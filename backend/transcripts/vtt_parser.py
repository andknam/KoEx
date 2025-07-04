import re

CHAR_LIMIT = 100
TOKEN_LIMIT = 50


# === Transcript Parsing ===
def clean_vtt_text(raw_text):
    # Remove inline timestamp and <c> tags
    return re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}><c>|</c>", "", raw_text)


def time_str_to_seconds(s: str) -> float:
    h, m, rest = s.split(":")
    sec, ms = rest.split(".")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def parse_vtt_file(vtt_path):
    with open(vtt_path, encoding="utf-8") as f:
        lines = f.readlines()

    raw_segments = []
    curr = {}
    timestamp_pattern = re.compile(
        r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})"
    )

    for line in lines:
        line = line.strip()

        match = timestamp_pattern.match(line)
        if match:
            if curr.get("text") and curr["text"].strip():
                raw_segments.append(curr)
                curr = {}

            curr["start"] = match.group(1)
            curr["end"] = match.group(2)
            curr["text"] = ""
        elif line and "text" in curr:
            cleaned = clean_vtt_text(line)
            curr["text"] += cleaned + " "

    if curr.get("text") and curr["text"].strip():
        raw_segments.append(curr)

    for seg in raw_segments:
        seg["text"] = seg["text"].strip()
        seg["start"] = time_str_to_seconds(seg["start"])
        seg["end"] = time_str_to_seconds(seg["end"])

    return chunk_by_sentences(raw_segments)


# === Sentence-aware Chunking ===
def chunk_by_sentences(segments):
    chunks = []
    current_chunk = {"text": "", "start": None, "end": None}

    for seg in segments:
        sentences = split_into_sentences(seg["text"])
        for sentence in sentences:
            if not sentence.strip():
                continue

            # fix overlap between sentence chunks
            # E.g., line 1: "이 제품은 진짜 좋아요.", line 2: "진짜 좋아요. 정말 편해요."
            sentence = strip_overlap(current_chunk["text"], sentence)
            sentence = strip_fuzzy_overlap(current_chunk["text"], sentence)

            sentence_token_count = count_tokens(sentence)
            sentence_char_count = len(sentence)

            if current_chunk["text"]:
                combined_text = f"{current_chunk['text']} {sentence}".strip()
                combined_token_count = count_tokens(combined_text)
                combined_char_count = len(combined_text)
            else:
                combined_text = sentence
                combined_token_count = sentence_token_count
                combined_char_count = sentence_char_count

            if combined_token_count > TOKEN_LIMIT or combined_char_count > CHAR_LIMIT:
                chunks.append(
                    {
                        "text": polish_text(current_chunk["text"]),
                        "start": current_chunk["start"],
                        "end": current_chunk["end"],
                    }
                )
                current_chunk = {
                    "text": sentence,
                    "start": seg["start"],
                    "end": seg["end"],
                }
            else:
                if not current_chunk["text"]:
                    current_chunk["start"] = seg["start"]
                current_chunk["text"] = combined_text
                current_chunk["end"] = seg["end"]

    if current_chunk["text"]:
        chunks.append(
            {
                "text": polish_text(current_chunk["text"]),
                "start": current_chunk["start"],
                "end": current_chunk["end"],
            }
        )

    return clean_chunk_overlaps(chunks)


# === Overlap Handling ===
def strip_overlap(prev_text, next_text, window=5):
    prev_words = prev_text.split()
    next_words = next_text.split()
    for i in range(window, 0, -1):
        if prev_words[-i:] == next_words[:i]:
            return " ".join(next_words[i:])
    return next_text


def strip_fuzzy_overlap(prev: str, curr: str, max_len: int = 50) -> str:
    """
    Strips the longest overlapping prefix in `curr` that matches the suffix in `prev`.
    Operates on characters for fuzzy Korean alignment.
    """
    for i in range(min(len(prev), len(curr), max_len), 10, -1):
        if prev[-i:] == curr[:i]:
            return curr[i:].strip()
    return curr


def split_into_sentences(text):
    pattern = re.compile(r"(.*?(?:니다|어요|예요|다|요|\.|\!|\?))(?=\s|$)")
    matches = pattern.findall(text)
    remainder = pattern.sub("", text).strip()
    if remainder:
        matches.append(remainder)
    return matches


# === Token Estimation ===
def count_tokens(text):
    return len(re.findall(r"\w+|[가-힣]", text))


# === Text Cleaning ===
def remove_bracket_tags(text):
    return re.sub(r"\[[^\]]+\]", "", text)


# using n-gram size 2-5
def remove_redundant_phrases(text, max_phrase_len=5):
    words = text.split()
    seen_phrases = set()
    deduped_words = []
    i = 0

    while i < len(words):
        found_duplicate = False
        for size in reversed(range(2, max_phrase_len + 1)):
            if i + size > len(words):
                continue
            phrase = tuple(words[i : i + size])
            if phrase in seen_phrases:
                i += size
                found_duplicate = True
                break

        if not found_duplicate:
            deduped_words.append(words[i])
            for size in range(2, max_phrase_len + 1):
                if i - size + 1 >= 0:
                    seen_phrases.add(tuple(words[i - size + 1 : i + 1]))
            i += 1

    return " ".join(deduped_words)


# matching consecutive non-space characters
def remove_duplicate_phrases_rough(text):
    for size in range(2, 6):
        pattern = re.compile(rf"(\S{{{size}}})\s*\1+")
        text = pattern.sub(r"\1", text)
    return text


def polish_text(text):
    text = remove_bracket_tags(text)
    text = remove_duplicate_phrases_rough(text)
    text = remove_redundant_phrases(text)
    return text.strip()


# === Post-chunk Deduplication ===
def clean_chunk_overlaps(chunks, max_overlap_len=12):
    if not chunks:
        return []

    cleaned = [chunks[0]]
    for i in range(1, len(chunks)):
        prev = cleaned[-1]["text"]
        curr = chunks[i]["text"]

        for w in range(max_overlap_len, 2, -1):
            prev_suffix = " ".join(prev.split()[-w:])
            if curr.startswith(prev_suffix):
                curr = curr[len(prev_suffix) :].strip()
                break

        cleaned.append({**chunks[i], "text": polish_text(curr)})

    return cleaned
