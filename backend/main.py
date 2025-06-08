from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.romanizer import romanize
# from backend.hanja_utils.utils import decompose_korean_word

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/analyze")
def analyze(word: str):
    return {
        "romanization": romanize(word),
        "decomposition": "...",
        "definition_kr": "...",
        "definition_en": "...",
    }