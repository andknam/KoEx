from fastapi import APIRouter, HTTPException
from backend.transcripts.youtube_utils import get_parsed_transcript
from backend.vector.qdrant_wrapper import embed_and_upsert
from backend.gpt.openai_client import OpenAIClient

router = APIRouter()
openai_client = OpenAIClient.get_client()

router = APIRouter()


@router.get("/transcript")
def get_transcript(videoUrl: str):
    try:
        chunks = get_parsed_transcript(videoUrl)
        embed_and_upsert(chunks, get_embedding)

        return chunks

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_embedding(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small", input=[text]
    )
    return response.data[0].embedding