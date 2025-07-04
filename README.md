# KoEx

Analyze Korean, search across YouTube. 

Powered by **GPT**, **Qdrant**, and *custom grammar* + *romanization* rules

<!-- ![KoEx Demo](./docs/koex-language-analysis.gif) -->

## Features

### Language Analysis Engine
- **Custom interlinear romanization** with character-level segmentation
- **Extraction of meaningful Korean words** with part-of-speech tags, English definitions, and example Korean sentences
- **Korean-to-Hanja conversion**, with:
  - Per-character annotations: *Pinyin*, *훈음*, and *English gloss*
- Linguistic Processing Pipeline
  - Idiom / 사자성어 detection using GPT
  - Auxiliary grammar grouping (i.e. `하고 싶다, 할 수 있다, 하겠다`)
    - **YAML-configured grammar rule engine** for scalability and easy rule expansion
  - Morphological (meaning) recombination (i.e. `실천/NNG + 하/XSV + 다/EC → 실천하다`)
  - Morphophonlogical (sound) contraction (i.e. `하 + 였 → 했`)
  - Stopword removal / token exclusion

### YouTube Transcript Interface

- Embedded video player with live transcript sync
- Click any subtitle to trigger:
  - Inline sentence gloss + Hanja annotations
  - **Semantic search** across other videos
    - Powered by OpenAI `text-embedding-3-small` embeddings + Qdrant Vector DB
    - Displays: timestamp, subtitle, source video, and relevance score
    - Jump-to-timestamp enabled for same-video matches
    
### Deep Dives
- [Language Analysis](./dpcs/language-analysis.md)
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