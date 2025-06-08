import CharacterBreakdown from './CharacterBreakdown';

export default function ResultBlock({ result }: { result: any }) {
  return (
    <div className="bg-white p-4 rounded shadow space-y-4">
      <div>
        <p className="font-semibold">Korean Definition:</p>
        <p>{result.koreanDef}</p>
      </div>
      <div>
        <p className="font-semibold">English Definition:</p>
        <p>{result.englishDef}</p>
      </div>
      <div>
        <p className="font-semibold">Romanization:</p>
        <p>{result.romanized}</p>
      </div>
      {result.example && (
        <div>
          <p className="font-semibold">Example Sentence:</p>
          <p>{result.example.sentence}</p>
          <p className="text-sm text-gray-600">
            "{result.example.translation}"
          </p>
        </div>
      )}
      <CharacterBreakdown characters={result.characters} />
    </div>
  );
}
