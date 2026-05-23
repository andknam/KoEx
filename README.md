# KoEx

**Analyze Korean. Search YouTube.**

Powered by **GPT**, **Qdrant**, and *custom grammar* + *romanization* rules

https://github.com/user-attachments/assets/3c63d1ed-d8bc-4b5a-929a-f16987fdd863

## Features

### 🧠 Language Analyzer
- Syllable-level romanization with interlinear output
- GPT-powered glossing, definitions, and 사자성어 (idiom) detection
- Korean-to-Hanja conversion with Pinyin, 훈음, and English
- Rule-based grammar chunking and recombination engine

### 📺 YouTube Search Interface
- Embedded video player with live transcript sync
- Clicking a subtitle:
  - Triggers inline glossing + Hanja annotation
  - Runs semantic search via OpenAI + Qdrant
  - Enables jump-to-timestamp for matching results
    
### Deep Dives
- [Language Analysis](./docs/language-analysis.md)
- [YouTube Player](./docs/youtube-player.md)
- [Semantic Search](./docs/semantic-search.md)

## Application Flow

The frontend sends Korean text to `GET /analyze-stream` as a server-sent events stream. The backend emits progress messages while it builds the final analysis payload.

1. `backend/main.py` receives the text and starts `analyze_generator`.
2. `filter_korean_tokens` preprocesses text, protects known 사자성어 with placeholders, tokenizes with Komoran, applies YAML auxiliary grammar rules, groups derived forms, restores idioms, and filters for meaningful content tokens.
3. `extract_candidate_korean_words` keeps noun/verb/adjective candidates, then `tag_if_derived_by_substring` marks derived words against shorter base forms.
4. `select_base_korean_words` sends base words to the Hanja batcher for Hanja, Pinyin, 훈음, and English annotations.
5. `select_definition_words` sends derived or standalone Korean words to the GPT analyzer for sentence glossing and word definitions.
6. `romanize` generates the romanized sentence locally.
7. `build_analysis_result` combines gloss, romanization, Hanja annotations, and word definitions, then streams the final JSON result back to the frontend.

The YouTube flow uses the same analyzer after a transcript line is selected. Transcript routes fetch and parse subtitles, and semantic search routes query Qdrant for related transcript chunks.

## Roadmap
- [ ] Word saving + graph visualization (shared Hanja network)
- [ ] Realtime visualization of token merging/chunking
- [ ] Audio playback of glossed sentences
- [ ] Support for stroke order animations

## Tech Stack

- **Frontend**: React, TypeScript, TailwindCSS
- **Backend**: FastAPI, OpenAI API, Qdrant
- **Linguistic Engine**: KoNLPy (Komoran), YAML rules
