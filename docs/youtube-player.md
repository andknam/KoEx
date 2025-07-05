# Youtube Player

This feature lets users input a YouTube link, play the video, and interact with a synchronized transcript. As the video plays, the current subtitle is highlighted. Clicking on a subtitle triggers a language analysis directly below the selected line. 

## Architecture

Frontend Components
- `YouTubePlayer`: embeds the video and tracks current timestamp
- `TranscriptViewer`: renders subtitles; clicking on a subtitle triggers analysis
- `TranscriptAnalysis`: streams progress messages + displays the result of `/analyze-stream`
- `SemanticMatchSidebar`: shows top-k semantically similar subtitles as cards
- `ScrollableWordCards`: displays Hanja annotations with Pinyin, 훈음, and English

Backend Endpoints
- `/transcript`: downloads and preprocesses `.vtt` subtitles
- `/analyze-stream`: performs language analysis
- `/search`: embeds subtitle and retrieves top-k semantic matches from Qdrant

Flow
1. User provides a YouTube link and presses **Load**
2. Subtitles are parsed and segmented into sentence-level chunks
3. The current subtitle is highlighted in sync as the video plays
4. Clicking a subtitle:
  - Sends a request to `/analyze-stream`
    - Streams progress messages inline under subtitle
    - Displays gloss and Hanja cards on completion
  - Sends a request to `/search`
    - Embeds subtitle, retrieves semantic matches from Qdrant
    - Displays related subtitles to the right side of the player

## Design Decisions

### 1. Progressive Analysis via SSE
We use Server-Sent Events to stream progress messages to the user. This gives the user feedback and avoids waiting without notice while the backend applies grammar chunking + performs GPT calls.

### 2. Why Not Precompute All Chunks?
Precomputing all subtitle chunks would:
- Delay transcript rendering
- Clutter the UI with output
- Increase GPT usage and cost

Instead, we only perform analysis when the user clicks on a subtitle.
