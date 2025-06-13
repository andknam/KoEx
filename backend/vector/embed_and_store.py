import json
import hashlib
from pathlib import Path
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from backend.gpt.openai_client import OpenAIClient

# === Config ===
COLLECTION_NAME = "gajiroc_interview_chunks"
VECTOR_DIM = 1536
JSON_PATH = Path("transcripts/youtube/parsed/gajiroc_interview_video_chunks.json")
QDRANT_PATH = Path("qdrant_storage")

# === Load transcript chunks ===
with open(JSON_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

# === Initialize OpenAI + Qdrant clients ===
openai_client = OpenAIClient.get_client()
qdrant = QdrantClient(path=str(QDRANT_PATH))

# === Create Qdrant collection if it doesn't exist ===
if not qdrant.collection_exists(collection_name=COLLECTION_NAME):
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
    )

# === Embed & Insert Chunks ===
def get_embedding(text: str) -> list[float]:
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=[text]
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"[ERROR] Failed to embed: {e}")
        return [0.0] * VECTOR_DIM  # Fallback

def hash_id(text: str, start: str) -> str:
    return hashlib.md5((text + start).encode("utf-8")).hexdigest()

points = []
for chunk in tqdm(chunks, desc="Embedding and inserting"):
    chunk_id = hash_id(chunk["text"], chunk["start"])
    embedding = get_embedding(chunk["text"])
    points.append(PointStruct(
        id=chunk_id,
        vector=embedding,
        payload={
            "text": chunk["text"],
            "start": chunk["start"],
            "end": chunk["end"]
        }
    ))

qdrant.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print("✅ All chunks embedded and stored in Qdrant!")
