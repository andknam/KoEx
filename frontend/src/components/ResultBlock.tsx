import KoreanBreakdown from './KoreanBreakdown';
import ScrollableWordCards from './ScrollableWordCards';
// import { ResultType } from '../types/resultTypes';

export default function ResultBlock({ result }: { result: any }) {
  return (
    <div className="bg-white p-4 rounded shadow space-y-4">
      <h1 className="text-2xl font-bold">{result.inputQuery}</h1>
      <p className="text-sm text-gray-500 italic">{result.romanized}</p>
      {result.sentenceGloss && result.sentenceGloss.trim() !== '' && (
        <p className="text-base mt-2">{result.sentenceGloss}</p>
      )}
      {/* <div>
        <p className="font-semibold">Korean Definition:</p>
        <p>{result.koreanDef}</p>
      </div> */}
      {/* <h2 className="font-semibold">Word Breakdown</h2> */}
      {result.koreanWords && <KoreanBreakdown words={result.koreanWords} />}
      {/* {result.example && (
        <div>
          <p className="font-semibold">Example Sentence:</p>
          <p>{result.example.sentence}</p>
          <p className="text-sm text-gray-600">
            "{result.example.translation}"
          </p>
        </div>
      )} */}
      {/* <h2 className="font-semibold">Hanja Breakdown</h2> */}
      {result.hanjaWords && <ScrollableWordCards words={result.hanjaWords} />}
    </div>
  );
}
