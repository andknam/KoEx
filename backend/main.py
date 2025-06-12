from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.gpt.korean_analyzer import analyze_korean_sentence

from backend.romanizer import romanize
from backend.hanja_utils.utils import korean_to_hanja

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# def test():
#     return [
#         {
#             "korean": "창의력",
#             "hanja": "創意力",
#             "characters": [
#             { "char": "創", "korean_gloss": "비롯할 창", "pinyin": "chuàng", "english_gloss": "create" },
#             { "char": "意", "korean_gloss": "뜻 의", "pinyin": "yì", "english_gloss": "idea" },
#             { "char": "力", "korean_gloss": "힘 력", "pinyin": "lì", "english_gloss": "power" }
#             ]
#         },
#         {
#             "korean": "문화",
#             "hanja": "文化",
#             "characters": [
#             { "char": "文", "korean_gloss": "글월 문", "pinyin": "wén", "english_gloss": "culture" },
#             { "char": "化", "korean_gloss": "될 화", "pinyin": "huà", "english_gloss": "transform" }
#             ]
#         },
#         {
#             "korean": "경제",
#             "hanja": "經濟",
#             "characters": [
#             { "char": "經", "korean_gloss": "지날 경", "pinyin": "jīng", "english_gloss": "manage" },
#             { "char": "濟", "korean_gloss": "건널 제", "pinyin": "jì", "english_gloss": "relieve" }
#             ]
#         },
#         {
#             "korean": "사랑",
#             "hanja": "愛",
#             "characters": [
#             { "char": "愛", "korean_gloss": "사랑 애", "pinyin": "ài", "english_gloss": "love" }
#             ]
#         },
#         {
#             "korean": "기술",
#             "hanja": "技術",
#             "characters": [
#             { "char": "技", "korean_gloss": "재주 기", "pinyin": "jì", "english_gloss": "skill" },
#             { "char": "術", "korean_gloss": "꾀 술", "pinyin": "shù", "english_gloss": "technique" }
#             ]
#         },
#                 {
#             "korean": "창의력",
#             "hanja": "創意力",
#             "characters": [
#             { "char": "創", "korean_gloss": "비롯할 창", "pinyin": "chuàng", "english_gloss": "create" },
#             { "char": "意", "korean_gloss": "뜻 의", "pinyin": "yì", "english_gloss": "idea" },
#             { "char": "力", "korean_gloss": "힘 력", "pinyin": "lì", "english_gloss": "power" }
#             ]
#         },
#         {
#             "korean": "문화",
#             "hanja": "文化",
#             "characters": [
#             { "char": "文", "korean_gloss": "글월 문", "pinyin": "wén", "english_gloss": "culture" },
#             { "char": "化", "korean_gloss": "될 화", "pinyin": "huà", "english_gloss": "transform" }
#             ]
#         },
#         {
#             "korean": "경제",
#             "hanja": "經濟",
#             "characters": [
#             { "char": "經", "korean_gloss": "지날 경", "pinyin": "jīng", "english_gloss": "manage" },
#             { "char": "濟", "korean_gloss": "건널 제", "pinyin": "jì", "english_gloss": "relieve" }
#             ]
#         },
#         {
#             "korean": "사랑",
#             "hanja": "愛",
#             "characters": [
#             { "char": "愛", "korean_gloss": "사랑 애", "pinyin": "ài", "english_gloss": "love" }
#             ]
#         },
#         {
#             "korean": "기술",
#             "hanja": "技術",
#             "characters": [
#             { "char": "技", "korean_gloss": "재주 기", "pinyin": "jì", "english_gloss": "skill" },
#             { "char": "術", "korean_gloss": "꾀 술", "pinyin": "shù", "english_gloss": "technique" }
#             ]
#         }
#     ]

@app.get("/analyze")
def analyze(input: str):
    # get all info about each hanja
    hanja_results = korean_to_hanja(input)

    # get all info about korean words
        # word, pos, meaning, example gloss
    # TODO: filter out determiners / particles / hashmap for specific verbs
    # i.e. 있 verb (conjugated form of 있다)
    korean_words = [entry["korean"] for entry in hanja_results]
    sentence_gloss, korean_word_info = analyze_korean_sentence(input, korean_words)

    # for testing
    # hanja_results = []
    # sentence_gloss = ''
    # korean_word_info = []

    return {
        "romanization": romanize(input),
        "hanja_words": hanja_results,
        "sentence_gloss": sentence_gloss,
        "word_info": korean_word_info,
        # "test": test,
    }