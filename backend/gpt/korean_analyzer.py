import json
import time
from backend.gpt.config import BATCH_SIZE

from backend.gpt.openai_client import OpenAIClient
from backend.gpt.utils import parse_response

client = OpenAIClient()

def build_input_gloss_prompt(input_text):
    return f"""
        You are a helpful Korean tutor. Given a Korean sentence, explain its overall meaning in English.
        If the sentence contains idioms, figurative expressions, or cultural context, explain them briefly as well.
        Keep the response very concise. Do not include the original input sentence in the result, unless you must use or explain specific words in the input.
        The style of the result should be similar to a machine translation or dictionary definition.

        Sentence: {input_text}

        Note: Here are a few examples.

            Korean: 고진감래의 의미를 깨달았다.  
            English: He came to understand the meaning of 'after hardship comes happiness.'

            Korean: 새로운 기술이 경제를 변화시키고 있다.  
            English: New technology is transforming the economy.

            Korean: 사랑은 때때로 아프기도 하다.  
            English: Love can sometimes be painful.

        Format your response as a string like this: "Love can sometimes be painful."
    """

def build_word_definition_prompt(words):
    return f"""
        You are a precise and structured assistant for Korean language learners.
        For each item in the list below, which may be a Korean word or idiom (including 사자성어), return:

        - The word as it appears
        - Its part of speech (e.g. noun, verb, idiom)
        - A simple English definition
        - A new Korean sentence using the word naturally (not the original sentence)

        Input list:
        {json.dumps(words, ensure_ascii=False)}

        Format your response as a JSON list like this:

        [
            {{
                "word": "고진감래",
                "pos": "noun (idiom)",
                "definition": "After hardship comes happiness",
                "example": "고진감래를 믿으며 어려운 시기를 견뎠다."
            }},
            {{
                "word": "의미",
                "pos": "noun",
                "definition": "meaning; significance",
                "example": "그 단어의 의미를 사전에서 찾아보았다."
            }},
            {{
                "word": "깨달았다",
                "pos": "verb (past tense of 깨닫다)",
                "definition": "realized; came to understand",
                "example": "나는 자신의 실수를 깨달았다."
            }}
        ]
    """

def analyze_korean_sentence(text, words, batch_size=BATCH_SIZE):
    sentence_gloss = None

    if len(words) > 1:
        gloss_prompt = build_input_gloss_prompt(text)
        content = client.call(gloss_prompt)
        sentence_gloss = parse_response(content)

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