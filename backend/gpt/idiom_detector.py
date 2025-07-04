from backend.gpt.openai_client import OpenAIClient
from backend.gpt.utils import parse_response

client = OpenAIClient()

def build_idiom_detection_prompt(input_text):
    return f"""
        You are a Korean language expert.

        Your task is to detect **idiomatic expressions** in the given Korean sentence. 
        An idiom is a commonly used fixed expression or 사자성어 (四字成語) that has a non-literal meaning or cultural significance. 

        Do NOT include generic clauses or sentences that are simply long or emotional. Focus only on actual idioms used in Korean language.

        Sentence: {input_text}

        Format your response as a list of strings: ["유유자적", "고진감래", "전화위복", "작심삼일"]
"""

def detect_idioms(text):
    prompt = build_idiom_detection_prompt(text)
    content = client.call(prompt)

    return parse_response(content)