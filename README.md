# KoEx

*Korean Explainer* is an AI-powered tool for Korean language learning.

## Features

### Language Analysis
- Korean-to-Hanja conversion
- Per-character annotations: Hanja, Pinyin, Korean gloss with 훈음, English meaning
- Custom inline romanization and glossing
- Smart tokenization via morpheme grouping and idiom preservation

### Search
- Semantic search across Korean YouTube transcripts and documents
- Vector search powered by OpenAI (`text-embedding-3-small`) + Qdrant

## Roadmap

### ✅ Completed
- [x] Romanization support
- [x] Komoran-based tokenization with surface-form preservation
- [x] Korean-to-Hanja conversion for words and idioms
- [x] Per-character glossing: 훈음, Pinyin, English meaning
- [x] Idiom-aware token merging (사자성어 handling)
- [x] Basic FastAPI backend with streaming response

### 🚧 In Progress
- [ ] Semantic + vector search (OpenAI + Qdrant)
- [ ] YouTube transcript extraction and chunking
- [ ] Frontend UI for results

### 🧩 Planned
- [ ] YouTube player with live analysis
- [ ] Full sentence contextual explanations (GPT-powered)
- [ ] Word saving + graph visualization (shared Hanja network)
- [ ] Voice gloss playback
- [ ] Support for stroke order animations
