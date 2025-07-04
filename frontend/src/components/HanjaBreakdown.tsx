export default function HanjaBreakdown({ characters }: { characters: any }) {
  return (
    <div>
      <ul className="space-y-2">
        {characters.map((c, idx) => (
          <li key={idx} className="flex items-center gap-4">
            <div className="text-2xl font-bold">{c.char}</div>
            <div>
              <p className="text-sm text-gray-600">{c.korean_gloss}</p>
              <p className="text-xs italic">
                {c.pinyin} – {c.english_gloss}
              </p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
