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
    For each of the following Korean words, return:

    1. The correct Hanja representation
    2. For each character, include:
    - Korean gloss in the format: [훈음] (e.g. "만들 창", not just "창")
    - Pinyin
    - English gloss

    Format your answer as a JSON list like this:

    [
    {{
        "korean": "...",
        "hanja": "...",
        "characters": [
        {{ "char": "...", "korean_gloss": "...", "pinyin": "...", "english_gloss": "..." }}
        ]
    }}
    ]

    Words: {json.dumps(words, ensure_ascii=False)}
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