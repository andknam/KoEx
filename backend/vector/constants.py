import os

COLLECTION_NAME = "youtube_transcript_chunks"
VECTOR_DIM = 1536
QDRANT_PATH = os.getenv("QDRANT_PATH", "qdrant_storage")
