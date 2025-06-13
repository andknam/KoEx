import re
from pathlib import Path
import json

CHAR_LIMIT = 80  # Max combined character length for merged chunks

# === Transcript Parsing ===
def clean_vtt_text(raw_text):
    # Remove inline timestamp and <c> tags
    return re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}><c>|</c>", "", raw_text)

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

    return merge_chunks(raw_segments)

# === Merging Chunks ===
def merge_chunks(segments):
    merged = []
    curr = None

    for seg in segments:
        seg_text = seg["text"].strip()

        if not curr:
            curr = seg.copy()
            continue

        combined_text = f"{curr['text']} {seg_text}".strip()

        if len(combined_text) > CHAR_LIMIT:
            merged.append(curr)
            curr = seg.copy()
        else:
            if seg_text not in curr["text"]:
                curr["end"] = seg["end"]
                curr["text"] = combined_text

    if curr:
        merged.append(curr)

    for m in merged:
        m["text"] = polish_text(m["text"])

    return merged

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

if __name__ == "__main__":
    vtt_file = Path("transcripts/youtube/raw/gajiroc_interview.ko.vtt")
    chunks = parse_vtt_file(vtt_file)

    for chunk in chunks[:5]:
        print(f"[{chunk['start']} → {chunk['end']}] {chunk['text']}")

    output_path = Path("transcripts/youtube/parsed/video_chunks.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
