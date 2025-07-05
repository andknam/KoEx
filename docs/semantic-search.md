## Semantic Search Overview

This pipeline powers KoEx’s subtitle semantic search using OpenAI embeddings and Qdrant vector search.

### Embeddings + Qdrant

**Embedding Strategy**
- **Model**: `text-embedding-3-small`  
- **Dimensions**: 1536  
- **Output**: unit-normalized vector  
- **Why this embedding?**
  - Supports multilingual input and tuned for semantic similarity
  - Fast and cheap (compared to `text-embedding-3-large`)
  - Good enough baseline for retrieval

**Qdrant Config**
- **Collection name**: `youtube_transcript_chunks`
- **Vector size**: 1536
- **Distance Metric**: Dot (= cosine for normalized vectors)
- **Payload**: `text`, `start`, `end`, `videoId`, `videoTitle`

### Transcript Chunking + Upsert Pipeline

We transform `.vtt` subtitles into semantically meaningful chunks and upsert via:

1. Download Subtitles 
   - Use `yt-dlp` to fetch auto-generated Korean subtitles
2. Text Cleanup
   - Remove timestamps and tags (e.g. `<c>`, `<00:01:23.456>`)
3. Convert Timestamp
   - Convert VTT times → float seconds (e.g. `00:01:23.456` → `83.456`)
4. Sentence Segmentation
   - Regex-based split on Korean endings: `다`, `요`, `니다`, `.`, `!`, `?`, etc.
5. Chunk Merging
   - Merge short sentences while considering:
     - `TOKEN_LIMIT = 50`
     - `CHAR_LIMIT = 100`
6. Strip Overlap
    - Remove duplicated or overlapping phrases across chunks (e.g. `...날씨가 좋다/날씨가 좋다...` --> `...날씨가 좋다/`)
    - Handle fuzzy overlaps (e.g. `...공부하고 싶어요/하고 싶어요...` --> `...공부하고 싶어요/`)
      - Useful when phrases are not perfectly tokenized 
7. Final Polish
   - Remove bracket tags (e.g. `[음악]`)
   - De-duplicate repeated character sequences and n-grams (e.g. `그 그 그` --> `그`)
8. Qdrant Upsert
   - After saving chunked subtitles as a parsed `.json`, we embed each chunk and upsert into Qdrant
      - `chunk_id` = md5 hash of `{videoId}-{start:.2f}` for stable, deduplicated id

### Query Flow

1. User clicks on a subtitle
2. KoEx embeds the subtitle chunk and sends it to `/search`
3. Qdrant retrieves top-k semantically similar chunks
4. Related results are rendered on the right side of the YouTube player

### Future Improvements
- Replace regex sentence splitting with a Korean POS tagger (e.g. EF + SF patterns)
- Consider BAAI/BGE-M3 or other higher quality multilingual embeddings
- Add payload metadata fields to support more advanced filtering (e.g. `lang = "ko"`)
