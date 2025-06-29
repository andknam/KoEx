# KoEx

*Korean Explainer* is an AI-powered tool for Korean language learning.

![KoEx Demo](./docs/koex-language-analysis.gif)

## Features

### Language Analysis
- Custom interlinear romanization with morpheme-level separation
- Extraction of meaningful Korean words with part-of-speech tags, Korean definitions, and example sentences
- Korean-to-Hanja conversion
  - Per-Hanja annotations: Pinyin, 훈음, and English gloss
- Smart tokenization via custom rule-based chunking
  - Idiom (사자성어) and fixed expression preservation
  - Auxiliary grammar grouping (i.e. 하고 싶다, 할 수 있다, 나가야 하다)
  - Morphological recombination (i.e. 변화/NNG + 하/XSV → 변화하다)
  - Contraction normalization (i.e. 봤어요 → 보다 + 았어요)
  - Stopword removal
  - YAML-configured grammar rule engine for scalability and easy rule expansion

### Search

![Semantic Search Pipeline](./docs/semantic-search-pipeline.png)

- Semantic search across Korean YouTube transcripts
  - Transcripts are automatically cleaned, deduplicated, and chunked
  - Overlapping and repeated phrases are removed
- Vector search powered by OpenAI (`text-embedding-3-small`) + Qdrant


### YouTube Player

- Embedded video player with live transcript sync
- Click any subtitle chunk to trigger a language analysis
  - Sentence gloss + inline Hanja annotations (with Pinyin + gloss)

### Deep Dives
- [YouTube Player](./docs/youtube-player.md)

## Roadmap

### 🚧 In Progress
- [x] Expand idiom + fixed expression detection
- [x] Handle negation patterns in verbs (i.e. -지 않다, -지 못하다) 
- [x] Semantic + vector search (OpenAI + Qdrant)
- [x] YouTube player with live analysis
- [ ] Update semantic search UI with richer metadata

### 🧩 Planned
- [ ] Full sentence contextual explanations (GPT-powered)
- [ ] Word saving + graph visualization (shared Hanja network)
- [ ] Voice playback of glossed sentences
- [ ] Support for stroke order animations
- [ ] Handle honorifics
- [ ] Support more complex grammar: conjunctions, quotatives, and adnominal forms (i.e. -지만, -다고 하다, -는 것)
- [ ] Improve parsing for numeral + counter units
