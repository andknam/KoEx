from backend.gpt.openai_client import OpenAIClient

client = OpenAIClient()


def build_spacing_prompt(text: str) -> str:
    return f"""
Add natural Korean spacing only.
Do not rewrite words, punctuation, or meaning.
Return only the corrected Korean text.

Text: {text}
"""


def normalize_korean_spacing(text: str) -> str:
    content = client.call(
        build_spacing_prompt(text),
        model="gpt-4o-mini",
        temperature=0.0,
    )

    if not content:
        return text

    return content.strip().strip('"')
