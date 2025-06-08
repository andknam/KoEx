import os
import json
import time
import re
from openai import OpenAI

from dotenv import load_dotenv

# Go up one directory to load the shared root-level .env
env_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path=env_path)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def build_prompt(words):
    return f"""
    You are an expert in Korean and Classical Chinese. For each item in the list below, which may be a Korean word or idiom (including 사자성어), return:

    1. If the word **has a valid Hanja representation**, return:
        - The Hanja form of the **entire word or idiom**
        - A character-by-character breakdown of the Hanja, including:
            - Korean gloss in the format: [훈음] (e.g., "만들 창")
            - Pinyin
            - English gloss

    2. If the word **does not have a Hanja origin** (i.e., it is a native Korean word or loanword), return:
        - `"hanja": ""`
        - `"characters": []`

    Input list:
    {json.dumps(words, ensure_ascii=False)}

    Format your response as a JSON list like this:

    [
    {{
        "korean": "유유자적",
        "hanja": "悠悠自適",
        "characters": [
        {{ "char": "悠", "korean_gloss": "멀 유", "pinyin": "yōu", "english_gloss": "distant" }},
        {{ "char": "悠", "korean_gloss": "멀 유", "pinyin": "yōu", "english_gloss": "leisurely" }},
        {{ "char": "自", "korean_gloss": "스스로 자", "pinyin": "zì", "english_gloss": "self" }},
        {{ "char": "適", "korean_gloss": "맞을 적", "pinyin": "shì", "english_gloss": "suitable" }}
        ]
    }},
    {{
        "korean": "요즘",
        "hanja": "",
        "characters": []
    }}
    ]
    """

def call_openai(prompt, model="gpt-4o", retries=2):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a precise linguistic assistant."},
                {"role": "user", "content": prompt}
            ])
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            time.sleep(1)
    return None

def clean_json_response(text):
    """
    Extracts the first JSON code block (```json ... ```) or falls back to raw text.
    """
    # Try to extract content inside ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return text.strip()  # Fallback: try parsing whole response as-is

def parse_response(content):
    try:
        cleaned = clean_json_response(content)
        return json.loads(cleaned)
    except Exception as e:
        print("⚠️ Failed to parse JSON. Error:", e)
        print("Raw content:")
        print(content)
        return None


def generate_hanja_for_words(words, batch_size=5):
    result = []
    for i in range(0, len(words), batch_size):
        batch = words[i:i+batch_size]
        prompt = build_prompt(batch)
        content = call_openai(prompt)
        data = parse_response(content)
        if data:
            result.extend(data)
        time.sleep(1)  # to be respectful
    return result