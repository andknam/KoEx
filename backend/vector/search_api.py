from fastapi import APIRouter, Query
from backend.gpt.openai_client import OpenAIClient
from backend.vector.qdrant_wrapper import search 

router = APIRouter()

@router.get("/search")
def semantic_search(q: str = Query(..., description="Search query")):
    client = OpenAIClient.get_client()
    try:
        embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=[q]
        ).data[0].embedding
    except Exception as e:
        return {"error": f"Embedding failed: {str(e)}"}

    try:
        results = search(query_vector=embedding, top_k=5)
    except Exception as e:
        return {"error": f"Qdrant search failed: {str(e)}"}

    print(f"Search query: {q}")
    print(f"Top hits: {[hit.payload['text'] for hit in results]}")
    print("Raw scores:", [hit.score for hit in results])

    return [
        {
            "text": hit.payload["text"],
            "start": hit.payload["start"],
            "end": hit.payload["end"],
            "score": hit.score
        }
        for hit in results
    ]