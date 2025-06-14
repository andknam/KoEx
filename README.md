# KoEx

*Korean Explainer* is an AI-powered tool for Korean language learning.

## Features

### Language Analysis
- Korean-to-Hanja conversion
- Per-character annotations: Hanja, Pinyin, Korean gloss with 훈음, English meaning
- Custom inline romanization and glossing
- Smart tokenization via morpheme grouping and idiom preservation
- Auxiliary grammar checking (i.e. 하고 싶다, 할 수 있다)
- Stopword removal

### Search
- Semantic search across Korean YouTube transcripts and documents
- Vector search powered by OpenAI (`text-embedding-3-small`) + Qdrant

## Roadmap

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
- [ ] Auxiliary grammar check for polite endings
