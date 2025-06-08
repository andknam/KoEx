type CharInfo = {
  char: string;
  hanja: string;
  pinyin: string;
  meaning: string;
  strokeGif: string;
};

export default function CharacterBreakdown({
  characters,
}: {
  characters: CharInfo[];
}) {
  return (
    <div>
      <p className="font-semibold">Characters:</p>
      <ul className="space-y-2">
        {characters.map((c, idx) => (
          <li key={idx} className="flex items-center gap-4">
            <div className="text-xl">{c.char}</div>
            <div>
              <div>Hanja: {c.hanja}</div>
              <div>Pinyin: {c.pinyin}</div>
              <div>Meaning: {c.meaning}</div>
            </div>
            {/* <img src={c.strokeGif} alt="stroke order" className="h-12 w-12" /> */}
          </li>
        ))}
      </ul>
    </div>
  );
}
