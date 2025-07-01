from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.gpt.openai_client import OpenAIClient
from backend.vector.qdrant_wrapper import search 

router = APIRouter()

@router.get("/search")
def semantic_search(query: str, videoId: str, start: float):
    client = OpenAIClient.get_client()
    try:
        embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        ).data[0].embedding
    except Exception as e:
        return {"error": f"Embedding failed: {str(e)}"}

    try:
        results = search(query_vector=embedding, top_k=10)
    except Exception as e:
        return {"error": f"Qdrant search failed: {str(e)}"}

    print(f"Chunk: {query}")
    print(f"Top hits: {[hit.payload['text'] for hit in results]}")
    print("Raw scores:", [hit.score for hit in results])

    response_items = []

    for hit in results:
        payload = hit.payload

        # skip if any fields missing
        if not all(k in payload for k in ["text", "start", "end", "videoId", "videoTitle"]):
            print(f"⚠️ Skipping hit due to missing fields: {payload}")
            continue

        # skip exact match with input query
        if payload["videoId"] == videoId and abs(payload["start"] - start) < 0.01:
            continue

        response_items.append({
            "text": payload["text"],
            "start": payload["start"],
            "end": payload["end"],
            "videoId": payload["videoId"],
            "videoTitle": payload["videoTitle"],
            "score": hit.score
        })

    return JSONResponse(content=response_items)