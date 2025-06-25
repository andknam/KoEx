import re
from pathlib import Path
import json

CHAR_LIMIT = 200  # Max combined character length for merged chunks
TOKEN_LIMIT = 300  # Approximate token threshold per chunk

# === Transcript Parsing ===
def clean_vtt_text(raw_text):
    # Remove inline timestamp and <c> tags
    return re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}><c>|</c>", "", raw_text)

def time_str_to_seconds(s: str) -> float:
    h, m, rest = s.split(":")
    sec, ms = rest.split(".")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000

def parse_vtt_file(vtt_path):
    with open(vtt_path, encoding='utf-8') as f:
        lines = f.readlines()

    raw_segments = []
    curr = {}
    timestamp_pattern = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})")

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

    return merge_chunks(raw_segments)

# === Merging Chunks ===
def merge_chunks(segments):
    merged = []
    curr = None

    for seg in segments:
        seg_text = seg["text"].strip()

        if len(seg_text) < 5:
            continue

        if not curr:
            curr = seg.copy()
            continue

        combined_text = f"{curr['text']} {seg_text}".strip()

        if (len(combined_text) > CHAR_LIMIT or count_tokens(combined_text) > TOKEN_LIMIT) and ends_in_sentence(curr["text"]):
            merged.append(curr)
            curr = seg.copy()
        else:
            seg_text = strip_overlap(curr["text"], seg_text)
            curr["end"] = seg["end"]
            curr["text"] = f"{curr['text']} {seg_text}".strip()

    if curr:
        merged.append(curr)

    for m in merged:
        m["text"] = polish_text(m["text"])

    return merged

# === Overlap Handling ===
def strip_overlap(prev_text, next_text, window=5):
    prev_words = prev_text.split()
    next_words = next_text.split()
    for i in range(window, 0, -1):
        if prev_words[-i:] == next_words[:i]:
            return ' '.join(next_words[i:])
    return next_text

# === Sentence-Aware Splitting ===
def ends_in_sentence(text):
    return text.endswith(("다", "요", "니다", ".", "!", "?"))

# === Token Estimation ===
def count_tokens(text):
    return len(text.split())

# === Text Cleaning ===
def remove_bracket_tags(text):
    return re.sub(r"\[[^\]]+\]", "", text)

def remove_duplicate_phrases_rough(text):
    for size in range(2, 6):
        pattern = re.compile(rf'(\S{{{size}}})\s*\1+')
        text = pattern.sub(r'\1', text)
    return text

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
            phrase = tuple(words[i:i+size])
            if phrase in seen_phrases:
                i += size
                found_duplicate = True
                break

        if not found_duplicate:
            deduped_words.append(words[i])
            for size in range(2, max_phrase_len + 1):
                if i - size + 1 >= 0:
                    seen_phrases.add(tuple(words[i - size + 1:i + 1]))
            i += 1

    return ' '.join(deduped_words)

def polish_text(text):
    text = remove_bracket_tags(text)
    text = remove_duplicate_phrases_rough(text)
    text = remove_redundant_phrases(text)
    
    return text.strip()
