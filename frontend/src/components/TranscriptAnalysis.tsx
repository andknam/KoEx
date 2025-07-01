import { useEffect, useState } from 'react';
import KoreanBreakdown from './KoreanBreakdown';
import ScrollableWordCards from './ScrollableWordCards';

type AnalysisResult = {
  romanization: string;
  sentence_gloss: string;
  hanja_words: any[];
  word_info: any[];
};

export default function TranscriptAnalysis({ chunk }: { chunk: string }) {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [progressMessages, setProgressMessages] = useState<string[]>([]);

  useEffect(() => {
    if (!chunk.trim()) return;

    setProgressMessages([]);
    setResult(null);

    setProgressMessages(['Starting analysis...']);

    const eventSource = new EventSource(
      `http://localhost:8000/analyze-stream?input=${encodeURIComponent(chunk)}`
    );

    eventSource.addEventListener('progress', (event: MessageEvent) => {
      setProgressMessages((prev) => [...prev, `${event.data}`]);
    });

    eventSource.addEventListener('result', (e) => {
      const data = JSON.parse(e.data);

      const filteredHanjaWords = data.hanja_words.filter(
        (item: any) => item.hanja && item.characters?.length > 0
      );

      setResult({ ...data, hanja_words: filteredHanjaWords });
      eventSource.close();
    });

    eventSource.onerror = (e) => {
      console.error('SSE error:', e);
      eventSource.close();
    };

    return () => eventSource.close();
  }, [chunk]);

  if (!result) {
    return (
      <div className="text-sm text-gray-500 mt-1">
        <ul className="space-y-1">
          {progressMessages.map((msg, i) => (
            <li key={i} className="animate-pulse">
              {msg}
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 -mt-1 border-none p-4 text-sm space-y-3 -ml-2.5">
      <div>
        <p className="text-base">{result.sentence_gloss}</p>
      </div>
      {/* {result.word_info && <KoreanBreakdown words={result.word_info} />} */}

      {result.hanja_words.length > 0 && (
        <div className="space-y-1">
          <ScrollableWordCards words={result.hanja_words} />
        </div>
      )}
    </div>
  );
}
