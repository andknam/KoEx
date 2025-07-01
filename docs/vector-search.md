## Semantic Search Overview

This pipeline powers KoEx’s subtitle-aware semantic search using OpenAI embeddings and Qdrant vector search.

---

### Embedding Strategy

- **Model**: `text-embedding-3-small`  
- **Dimensions**: 1536  
- **Output**: unit-normalized vector  
- **Why this embedding?**
  - Supports multilingual input and tuned for semantic similarity
  - Fast and cheap (compared to `text-embedding-3-large`)
  - Good enough baseline for retrieval

---

### Transcript Chunking Pipeline

We transform `.vtt` subtitles into semantically meaningful chunks via:

1. Download Subtitles 
   - Use `yt-dlp` to fetch auto-generated Korean subtitles
2. Text Cleanup
   - Remove timestamps and tags (i.e. `<c>`, `<00:01:23.456>`)
3. Convert Timestamp
   - Convert VTT times → float seconds (i.e. `00:01:23.456` → `83.456`)
4. Sentence Segmentation
   - Regex-based split on Korean endings: `다`, `요`, `니다`, `.`, `!`, `?`, etc.
5. Chunk Merging
   - Merge short sentences while considering:
     - `TOKEN_LIMIT = 50`
     - `CHAR_LIMIT = 160`
6. Strip Overlap
    - Remove duplicated or overlapping phrases across chunks
    - Handle fuzzy overlaps (i.e. "좋아요. 정말 편해요." vs "정말 편해요.")
7. Final Polish
   - Remove bracket tags (`[음악]`)
   - De-duplicate repeated character sequences and n-grams

---

### Query Flow

1. User clicks “See Similar” on a subtitle
2. Koex embeds the subtitle chunk
3. Sends query to `/search`
4. Qdrant retrieves top-k similar chunks
5. Related results are rendered on the side of the youtube player

---

### Future Improvements
- Replace regex sentence splitting / fixed chunking with proper sentence/morpheme-based boundaries
- Consider BAAI/BGE-M3 or other multilingual embeddings