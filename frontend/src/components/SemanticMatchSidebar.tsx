type MatchEntry = {
  text: string;
  start: number;
  videoTitle: string;
  videoId: string;
  score: number;
};

type Props = {
  matches: MatchEntry[];
  currentVideoId: string;
  isLoading: boolean;
  onJump: (start: number) => void;
};

const SemanticMatchSidebar = ({
  matches,
  currentVideoId,
  isLoading,
  onJump,
}: Props) => {
  if (isLoading) {
    return (
      <div className="text-sm text-gray-400">
        Searching for similar chunks...
      </div>
    );
  }

  if (matches.length) {
    return (
      <div className="space-y-3">
        {matches.map((match, idx) => {
          const isCurrent = match.videoId === currentVideoId;
          return (
            <div
              key={idx}
              className={`p-3 rounded-md border ${
                isCurrent ? 'hover:bg-gray-50 cursor-pointer' : ''
              } text-gray-500`}
              onClick={() => isCurrent && onJump?.(match.start)}
            >
              <span className="text-sm text-gray-400 mr-2">
                {formatTimestamp(match.start)}
              </span>
              {match.text}
              <div className="mb-2" />
              <div className="text-xs text-gray-400 flex justify-between">
                <span className="italic">
                  {isCurrent
                    ? 'Current video (click to jump)'
                    : match.videoTitle}
                </span>
                <span className="text-right text-gray-500 font-mono">
                  {match.score.toFixed(2)}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  return null;
};

function formatTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export default SemanticMatchSidebar;
