import re
import json

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