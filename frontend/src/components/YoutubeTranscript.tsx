import { useState, useEffect, useRef } from 'react';
import YouTube from 'react-youtube';
import axios from 'axios';
import TranscriptAnalysis from './TranscriptAnalysis';
import SemanticMatchSidebar from './SemanticMatchSidebar';

// Types
type TranscriptEntry = {
  text: string;
  start: number;
  end: number;
  videoId: string;
};

type Props = {
  url: string; // passed in from Tabs.tsx
};

// Helper
function extractVideoId(url: string): string | null {
  const match = url.match(/(?:v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  return match ? match[1] : null;
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Player component
const YouTubePlayer = ({
  videoId,
  onTimeUpdate,
}: {
  videoId: string;
  onTimeUpdate: (t: number) => void;
}) => {
  const playerRef = useRef<any>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      const time = playerRef.current?.getCurrentTime?.();
      if (typeof time === 'number') {
        onTimeUpdate(time);
      }
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <YouTube
      videoId={videoId}
      onReady={(e) => (playerRef.current = e.target)}
      opts={{ playerVars: { rel: 0 } }}
    />
  );
};

// Transcript Viewer
const TranscriptViewer = ({
  transcript = [],
  currentTime,
  onSubtitleClick,
}: {
  transcript?: TranscriptEntry[];
  currentTime: number;
  onSubtitleClick?: (entry: TranscriptEntry) => void;
}) => {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const currentIndex = transcript.findIndex(
    (t) => currentTime >= t.start && currentTime < t.end
  );

  useEffect(() => {
    const el = containerRef.current?.querySelector(
      `[data-index="${currentIndex}"]`
    );
    if (el) {
      (el as HTMLElement).scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
    }
  }, [currentIndex]);

  // Now do conditional rendering AFTER all hooks
  if (!transcript || transcript.length === 0) {
    return (
      <div className="h-60 overflow-y-auto p-4 text-gray-500 text-sm italic">
        No transcript available for this video.
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="h-60 overflow-y-auto p-2 bg-gray-50 scrollbar-none text-lg"
    >
      {transcript.map((t, i) => {
        const isCurrent = i === currentIndex;
        const isContext = Math.abs(i - currentIndex) <= 2;
        if (!isCurrent && !isContext) return null;

        return (
          <div key={i} data-index={i} className="mb-2">
            <div
              className={`p-1 rounded max-w-[720px] cursor-pointer ${
                isCurrent ? 'bg-yellow-200 font-semibold' : 'text-gray-500'
              }`}
              onClick={() => {
                setActiveIndex(i === activeIndex ? null : i);
                onSubtitleClick?.(t);
              }}
            >
              <span className="text-sm text-gray-400 mr-2">
                {formatTime(t.start)}
              </span>
              {t.text}
            </div>

            <div className="max-w-[640px] overflow-hidden">
              {activeIndex === i && <TranscriptAnalysis chunk={t.text} />}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// Main Component
const YouTubeTranscript = ({ url }: Props) => {
  const [videoId, setVideoId] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [currentTime, setCurrentTime] = useState(0);
  const [semanticMatches, setSemanticMatches] = useState<TranscriptEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!url) return;

    const id = extractVideoId(url);
    if (!id) return;

    setVideoId(id);

    const fetchTranscript = async () => {
      try {
        const res = await axios.get(
          `http://localhost:8000/transcript?videoUrl=${encodeURIComponent(url)}`
        );
        console.log("Transcript response:", res.data); // ✅ ADD THIS
        if (res.data.length === 0) {
          console.warn("Transcript empty — possibly unavailable.");
        }
        setTranscript(res.data);
      } catch (err) {
        console.error('Failed to fetch transcript', err);
        setTranscript([]); 
      }
    };

    fetchTranscript();
  }, [url]);

  const handleSubtitleClick = async (entry: TranscriptEntry) => {
    try {
      // clear out the existing cards
      setSemanticMatches([]);
      setIsLoading(true);

      const query = encodeURIComponent(entry.text);
      const videoId = encodeURIComponent(entry.videoId);
      const start = encodeURIComponent(entry.start);
      
      const res = await fetch(
        `http://localhost:8000/search?query=${query}&videoId=${videoId}&start=${start}`
      );

      if (!res.ok) throw new Error("Search failed");

      const data = await res.json();
      setSemanticMatches(data);
    } catch (err) {
      console.error("Failed to fetch semantic matches", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleJumpTo = (start: number) => {
    const player = document.querySelector('iframe') as HTMLIFrameElement;
    player?.contentWindow?.postMessage(
      JSON.stringify({
        event: "command",
        func: "seekTo",
        args: [start, true],
      }),
      "*"
    );
  };

  return (
    <div className="flex flex-row w-full h-[620px]">
      <div className="flex flex-col w-[700px] space-y-4">
        {videoId && (
          <>
            <YouTubePlayer videoId={videoId} onTimeUpdate={setCurrentTime} />
            <div className="-ml-2.5">
              <TranscriptViewer
                transcript={transcript}
                currentTime={currentTime}
                onSubtitleClick={handleSubtitleClick}
              />
            </div>
          </>
        )}
      </div>

      <div className="min-w-[450px] pl-6 scrollbar-none overflow-y-auto">
        <SemanticMatchSidebar
          matches={semanticMatches}
          currentVideoId={videoId}
          isLoading={isLoading}
          onJump={handleJumpTo}
        />
      </div>
    </div>
  );
};

export default YouTubeTranscript;
