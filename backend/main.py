import json
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.gpt.hanja_batcher import generate_hanja_for_words
from backend.gpt.korean_analyzer import analyze_korean_sentence

from backend.language_analysis.linguistic_processing.filtering import (
    filter_korean_tokens,
)
from backend.language_analysis.word_extraction import (
    extract_candidate_korean_words,
    tag_if_derived_by_substring,
)

from backend.language_analysis.romanizer import romanize

from backend.vector import search_api
from backend.transcripts import transcript_api

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
app.include_router(transcript_api.router)


def extract_korean_word_candidates(input_text: str) -> list[dict]:
    tokens = filter_korean_tokens(input_text)
    print(f"{tokens=}")

    candidate_words = extract_candidate_korean_words(tokens)
    print(f"{candidate_words=}")

    tagged_candidates = tag_if_derived_by_substring(candidate_words)
    print(f"{tagged_candidates=}")
    return tagged_candidates


def select_base_korean_words(tagged_candidates: list[dict]) -> list[str]:
    base_words = [
        entry["korean"]
        for entry in tagged_candidates
        if not entry["is_derived"]
    ]
    print(f"{base_words=}")
    return base_words


def select_definition_words(tagged_candidates: list[dict]) -> list[str]:
    derived_base_forms = {
        entry["base_form"]
        for entry in tagged_candidates
        if entry["is_derived"]
    }

    definition_words = [
        entry["korean"]
        for entry in tagged_candidates
        if entry["is_derived"] or entry["korean"] not in derived_base_forms
    ]

    print(f"{definition_words=}")
    return definition_words


def build_analysis_result(
    sentence_gloss: str,
    romanized: str,
    hanja_words: list[dict],
    korean_word_info: list[dict],
) -> dict:
    return {
        "sentence_gloss": sentence_gloss,
        "romanization": romanized,
        "hanja_words": hanja_words,
        "word_info": korean_word_info,
    }


async def analyze_generator(input_text: str):
    # Step 1: Tokenize + tag candidate korean words with base / derived
    await asyncio.sleep(0.5)
    yield "event: progress\ndata: Tokenizing input...\n\n"
    await asyncio.sleep(0.25)
    yield "event: progress\ndata: Identifying idioms and meaningful Korean word candidates...\n\n"

    tagged_candidates = extract_korean_word_candidates(input_text)
    await asyncio.sleep(0.5)

    # Step 2: Generate hanja matches for base korean words
    yield "event: progress\ndata: Generating Hanja annotations for base Korean words...\n\n"

    base_korean_words = select_base_korean_words(tagged_candidates)
    hanja_words = generate_hanja_for_words(base_korean_words)
    await asyncio.sleep(0.5)

    # Step 3: Generate gloss and korean word information
    yield "event: progress\ndata: Creating sentence gloss and Korean word definitions...\n\n"

    derived_korean_words = select_definition_words(tagged_candidates)
    sentence_gloss, korean_word_info = analyze_korean_sentence(
        input_text, derived_korean_words
    )
    await asyncio.sleep(0.5)

    # Step 4: Romanization
    yield "event: progress\ndata: Generating romanization...\n\n"
    romanized = romanize(input_text)
    await asyncio.sleep(0.5)

    # Step 5: Finalizing
    yield "event: progress\ndata: Finalizing response...\n\n"

    result = build_analysis_result(
        sentence_gloss,
        romanized,
        hanja_words,
        korean_word_info,
    )

    yield f"event: result\ndata: {json.dumps(result, ensure_ascii=False)}\n\n"


@app.get("/analyze-stream")
async def analyze_stream(input: str):
    return StreamingResponse(analyze_generator(input), media_type="text/event-stream")
