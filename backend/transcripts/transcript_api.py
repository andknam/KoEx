from fastapi import APIRouter, Query, HTTPException
from backend.transcripts.youtube_utils import get_parsed_transcript

router = APIRouter()

@router.get("/transcript")
def get_transcript(videoUrl: str):
    try:
        return get_parsed_transcript(videoUrl)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))