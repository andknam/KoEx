import KoreanBreakdown from './KoreanBreakdown';
import ScrollableWordCards from './ScrollableWordCards';

export default function ResultBlock({ result }: { result: any }) {
  return (
    <div className="bg-white p-4 rounded shadow space-y-4">
      <h1 className="text-2xl font-bold">{result.inputQuery}</h1>
      <p className="text-sm text-gray-500 italic">{result.romanized}</p>
      {result.sentenceGloss && result.sentenceGloss.trim() !== '' && (
        <p className="text-base mt-2">{result.sentenceGloss}</p>
      )}
      {result.koreanWords && <KoreanBreakdown words={result.koreanWords} />}
      {result.hanjaWords && <ScrollableWordCards words={result.hanjaWords} />}
    </div>
  );
}
