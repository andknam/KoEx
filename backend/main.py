import json
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.gpt.korean_analyzer import analyze_korean_sentence
from backend.romanizer import romanize
from backend.hanja_utils.hanja_pipeline import korean_to_hanja
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

app.include_router(search_api.router, prefix="/api")

async def analyze_generator(input_text: str):
    yield "event: progress\ndata: Starting analysis...\n\n"

    # Step 1: Extract Hanja information
    yield "event: progress\ndata: Fetching Korean words...\n\n"
    hanja_results = korean_to_hanja(input_text)
    await asyncio.sleep(0.5) 

    # Step 2: POS tagging & glossing
    yield "event: progress\ndata: Analyzing sentence structure...\n\n"
    korean_words = [entry["korean"] for entry in hanja_results]
    sentence_gloss, korean_word_info = analyze_korean_sentence(input_text, korean_words)
    await asyncio.sleep(0.5)

    # Step 3: Romanization
    yield "event: progress\ndata: Generating romanization...\n\n"
    romanized = romanize(input_text)
    await asyncio.sleep(0.5)

    # Step 4: Finalizing
    yield "event: progress\ndata: Finalizing response...\n\n"
    await asyncio.sleep(0.3)

    result = {
        "sentence_gloss": sentence_gloss,
        "romanization": romanized,
        "hanja_words": hanja_results,
        "word_info": korean_word_info,
    }

    yield f"event: result\ndata: {json.dumps(result, ensure_ascii=False)}\n\n"


@app.get("/analyze-stream")
async def analyze_stream(input: str):
    return StreamingResponse(analyze_generator(input), media_type="text/event-stream")

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
