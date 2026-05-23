import json
import time
from backend.gpt.config import BATCH_SIZE

from backend.gpt.openai_client import OpenAIClient
from backend.gpt.utils import parse_response

client = OpenAIClient()

def build_prompt(words):
    return f"""
Return Hanja data as JSON for each Korean item.
If no Hanja origin, use "hanja": "" and "characters": [].

Items: {json.dumps(words, ensure_ascii=False)}

Format:
[
  {{
    "korean":"유유자적",
    "hanja":"悠悠自適",
    "characters":[
      {{"char":"悠","korean_gloss":"멀 유","pinyin":"yōu","english_gloss":"distant"}}
    ]
  }}
]
"""

def generate_hanja_for_words(words, batch_size=BATCH_SIZE):
    result = []
    for i in range(0, len(words), batch_size):
        batch = words[i:i+batch_size]
        prompt = build_prompt(batch)
        content = client.call(prompt)
        data = parse_response(content)

        if data:
            result.extend(data)
        time.sleep(1)  # to be respectful

    return result
