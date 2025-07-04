import json
import time
from backend.gpt.config import BATCH_SIZE

from backend.gpt.openai_client import OpenAIClient
from backend.gpt.utils import parse_response

client = OpenAIClient()

def build_prompt(words):
    return f"""
        You are an expert in Korean and Classical Chinese. 
        For each item in the list below, which may be a Korean word or idiom (including 사자성어), return:

        1. If the word **has a valid Hanja representation**, return:
            - The Hanja form of the **entire word or idiom**
            - A character-by-character breakdown of the Hanja, including:
                - Korean gloss in the format: [훈음] (e.g., "만들 창")
                - Pinyin
                - English gloss

        2. If the word **does not have a Hanja origin** (i.e., it is a native Korean word or loanword), return:
            - "hanja": ""
            - "characters": []

        Input list:
        {json.dumps(words, ensure_ascii=False)}

        Format your response as a JSON list like this:

        [
        {{
            "korean": "유유자적",
            "hanja": "悠悠自適",
            "characters": [
            {{
                "char": "悠", "korean_gloss": "멀 유", "pinyin": "yōu", "english_gloss": "distant"
            }},
            {{
                "char": "悠", "korean_gloss": "멀 유", "pinyin": "yōu", "english_gloss": "leisurely"
            }},
            {{
                "char": "自", "korean_gloss": "스스로 자", "pinyin": "zì", "english_gloss": "self"
            }},
            {{
                "char": "適", "korean_gloss": "맞을 적", "pinyin": "shì", "english_gloss": "suitable"
            }}
            ]
        }},
        {{
            "korean": "요즘",
            "hanja": "",
            "characters": []
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