import re

from backend.gpt.idiom_detector import detect_idioms


# remove non-Hangul
def preprocess_text(text: str) -> str:
    return re.sub(r"[^\uac00-\ud7a3\s]", "", text)


# trick used to avoid collison with regular symbols
# not split up by tokenizers
def generate_placeholder(idx: int) -> str:
    return f"＠＠{idx}"  # Full-width @ (U+FF20)


# detect idioms and replace them with safe placeholders
def replace_sajaseongeo_with_placeholders(text: str) -> tuple[str, dict]:
    idioms = set(detect_idioms(text))  # de-duplicate
    placeholder_map = {}

    for idx, phrase in enumerate(idioms):
        # match idiom followed by optional suffix (i.e. any non-whitespace char immediately after)
        pattern = re.compile(rf"{re.escape(phrase)}\S*")

        match = re.search(pattern, text)
        if match:
            placeholder = generate_placeholder(idx)
            text = re.sub(pattern, placeholder, text, count=1)
            placeholder_map[placeholder] = phrase

    return text, placeholder_map
