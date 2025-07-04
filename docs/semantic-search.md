## Semantic Search Overview

This pipeline powers KoEx’s subtitle-aware semantic search using OpenAI embeddings and Qdrant vector search.

### Embedding Strategy

- **Model**: `text-embedding-3-small`  
- **Dimensions**: 1536  
- **Output**: unit-normalized vector  
- **Why this embedding?**
  - Supports multilingual input and tuned for semantic similarity
  - Fast and cheap (compared to `text-embedding-3-large`)
  - Good enough baseline for retrieval

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
     - `CHAR_LIMIT = 100`
6. Strip Overlap
    - Remove duplicated or overlapping phrases across chunks (i.e. `...날씨가 좋다/날씨가 좋다...` --> `...날씨가 좋다/`)
    - Handle fuzzy overlaps (i.e. `...공부하고 싶어요/하고 싶어요...` --> `...공부하고 싶어요/`)
      - Useful when phrases are not perfectly tokenized 
7. Final Polish
   - Remove bracket tags (`[음악]`)
   - De-duplicate repeated character sequences and n-grams (i.e. `그 그 그` --> `그`)

### Query Flow

1. User clicks on a subtitle
2. Koex embeds the subtitle chunk
3. Sends query to `/search`
4. Qdrant retrieves top-k semantically similar chunks
5. Related results are rendered on the right side of the youtube player

### Future Improvements
- Replace regex sentence splitting with a Korean POS tagger and split based on final endings + sentence particles (i.e. EF + SF patterns)
- Consider BAAI/BGE-M3 or other multilingual embeddings