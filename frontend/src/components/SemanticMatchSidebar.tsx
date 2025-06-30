type MatchEntry = {
  text: string;
  start: number;
  score?: number; // optional for now
  video: string;
};

type Props = {
  matches: MatchEntry[];
};

const SemanticMatchSidebar = ({ matches }: Props) => {
  if (matches.length) {
    return (
      <div className="space-y-3">
        {matches.map((match, idx) => (
          <div
            key={idx}
            className="p-3 rounded-md border hover:bg-gray-50 cursor-pointer"
            onClick={() => onJump(match.start)}
          >
            <div className="text-sm text-gray-700 mb-1">
              {formatTimestamp(match.start)}
            </div>
            <div className="text-sm text-black">{highlight(match.text)}</div>
            <div className="text-sm text-black">{highlight(match.video)}</div>
          </div>
        ))}
      </div>
    );
  }
};

// Optional: format 62.34 -> 1:02
function formatTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

// Optional: highlight fuzzy keyword (stubbed)
function highlight(text: string): string {
  return text; // Replace later with real highlight logic
}

export default SemanticMatchSidebar;
