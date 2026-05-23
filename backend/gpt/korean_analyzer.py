import json
import time
from backend.gpt.config import BATCH_SIZE

from backend.gpt.openai_client import OpenAIClient
from backend.gpt.utils import clean_json_response, parse_response

client = OpenAIClient()

def build_input_gloss_prompt(input_text):
    return f"""
Translate this Korean sentence into concise natural English.
Explain idioms only if needed.
Return only the English sentence as plain text.

Sentence: {input_text}
    """

def build_word_definition_prompt(words):
    return f"""
For each Korean item, return JSON with:
word, pos, definition, example.
Use a new Korean example sentence, not the original sentence.

Items: {json.dumps(words, ensure_ascii=False)}

Format:
[
  {{"word":"고진감래","pos":"idiom","definition":"after hardship comes happiness","example":"고진감래를 믿으며 버텼다."}}
]
    """

def analyze_korean_sentence(text, words, batch_size=BATCH_SIZE):
    sentence_gloss = None

    if len(words) > 1:
        gloss_prompt = build_input_gloss_prompt(text)
        content = client.call(gloss_prompt)
        sentence_gloss = normalize_gloss_response(content)

    word_info = []
    for i in range(0, len(words), batch_size):
        batch = words[i:i+batch_size]
        prompt = build_word_definition_prompt(batch)
        content = client.call(prompt)
        batch_info = parse_response(content)
        if batch_info:
            word_info.extend(batch_info)
        time.sleep(1)  # to be respectful of rate limits

    return sentence_gloss, word_info


def normalize_gloss_response(content: str | None) -> str | None:
    if not content:
        return None

    stripped_content = content.strip()
    if stripped_content[:1] not in {'"', "{", "["}:
        return stripped_content

    try:
        parsed = json.loads(clean_json_response(stripped_content))
    except json.JSONDecodeError:
        return stripped_content.strip('"')

    if isinstance(parsed, str):
        return parsed

    if isinstance(parsed, dict):
        for key in ("translation", "english", "gloss", "sentence_gloss"):
            value = parsed.get(key)
            if isinstance(value, str):
                return value

    return stripped_content.strip('"')
