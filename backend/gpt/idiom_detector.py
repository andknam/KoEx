from backend.gpt.openai_client import OpenAIClient
from backend.gpt.utils import parse_response

client = OpenAIClient()

def build_idiom_detection_prompt(input_text):
    return f"""
Detect Korean idioms or 사자성어 in the sentence.
Return only a JSON array of strings.
If none, return [].

Sentence: {input_text}
"""

def detect_idioms(text):
    prompt = build_idiom_detection_prompt(text)
    content = client.call(prompt)

    return parse_response(content)
