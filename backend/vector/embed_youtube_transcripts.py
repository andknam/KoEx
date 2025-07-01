import json
from pathlib import Path

from backend.vector.qdrant_wrapper import embed_and_upsert
from backend.gpt.openai_client import OpenAIClient
from backend.vector.constants import VECTOR_DIM

TRANSCRIPTS_DIR = Path("backend/transcripts/youtube/parsed")
openai_client = OpenAIClient.get_client()


def get_embedding(text: str) -> list[float]:
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small", input=[text]
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"[ERROR] Failed to embed: {e}")
        return [0.0] * VECTOR_DIM


json_files = list(TRANSCRIPTS_DIR.glob("*.json"))

for path in json_files:
    print(f"\n📄 Processing: {path.name}")
    with open(path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    embed_and_upsert(chunks, get_embedding)

print("✅ All transcripts embedded and stored!")
