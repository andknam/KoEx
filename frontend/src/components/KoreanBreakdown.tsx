// type WordInfo = {
//     word: string;
//     pos: string;
//     definition: string;
//     example: string;
// };

export default function KoreanBreakdown({ words }: { words: any }) {
  if (!words || words.length === 0) {
    return <p className="text-sm text-gray-500">No words to display.</p>;
  }

  return (
    <div>
      <ul className="space-y-2">
        {words.map((w, idx) => (
          <li key={idx} className="flex items-start gap-4">
            <div className="text-lg font-bold w-32 shrink-0">{w.word}</div>
            <div className="space-y-1">
              <p className="text-sm text-gray-500">{w.pos}</p>
              <p className="text-sm">{w.definition}</p>
              <p className="text-xs text-gray-600 italic">예시: {w.example}</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
