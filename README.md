# KoEx

**Analyze Korean. Search YouTube.**
Powered by **GPT**, **Qdrant**, and *custom grammar* + *romanization* rules

<!-- ![KoEx Demo](./docs/koex-language-analysis.gif) -->

## Features

### 🧠 Language Analyzer
- Character-level romanization with interlinear output
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

## Roadmap
- [ ] Word saving + graph visualization (shared Hanja network)
- [ ] Realtime visualization of token merging/chunking
- [ ] Audio playback of glossed sentences
- [ ] Support for stroke order animations

## Tech Stack

- **Frontend**: React, TypeScript, TailwindCSS
- **Backend**: FastAPI, OpenAI API, Qdrant
- **Linguistic Engine**: KoNLPy (Komoran), YAML rules