from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter
from typing import List
import hashlib
import os

COLLECTION_NAME = "gajiroc_interview_chunks"
VECTOR_DIM = 1536
QDRANT_PATH = os.getenv("QDRANT_PATH", "qdrant_storage")

client = QdrantClient(path=QDRANT_PATH)

def ensure_collection():
    if not client.collection_exists(collection_name=COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
        )

def embed_and_upsert(chunks: List[dict], embed_fn):
    ensure_collection()
    points = []
    for chunk in chunks:
        chunk_id = hashlib.md5((chunk["text"] + chunk["start"]).encode("utf-8")).hexdigest()
        vector = embed_fn(chunk["text"])
        points.append(PointStruct(
            id=chunk_id,
            vector=vector,
            payload={
                "text": chunk["text"],
                "start": chunk["start"],
                "end": chunk["end"]
            }
        ))
    client.upsert(collection_name=COLLECTION_NAME, points=points)

def search(query_vector: List[float], top_k=5):
    ensure_collection()
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    return results
