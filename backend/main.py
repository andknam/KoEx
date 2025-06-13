from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.gpt.korean_analyzer import analyze_korean_sentence

from backend.romanizer import romanize
from backend.hanja_utils.utils import korean_to_hanja
from backend.vector import search_api

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_api.router)

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
