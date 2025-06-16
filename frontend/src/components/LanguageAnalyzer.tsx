import { useEffect, useState } from 'react';
import ResultBlock from './ResultBlock';

export default function LanguageAnalyzer({
  input,
  onDone,
}: {
  input: string;
  onDone: () => void;
}) {
  const [loading, setLoading] = useState(false);
  const [progressMessages, setProgressMessages] = useState<string[]>([]);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    if (!input.trim()) return;

    setLoading(true);
    setProgressMessages([]);
    setResult(null);

    setProgressMessages(["Starting analysis..."]);

    const eventSource = new EventSource(
      `http://localhost:8000/analyze-stream?input=${encodeURIComponent(input)}`
    );

    eventSource.addEventListener('progress', (event: MessageEvent) => {
      setProgressMessages((prev) => [...prev, event.data]);
    });

    eventSource.addEventListener('result', (event: MessageEvent) => {
      const data = JSON.parse(event.data);

      const filteredHanjaWords = data.hanja_words.filter(
        (item: any) =>
          item.hanja && item.characters && item.characters.length > 0
      );

      setResult({
        inputQuery: input,
        koreanDef: 'placeholder',
        sentenceGloss: data.sentence_gloss,
        romanized: data.romanization,
        example: {
          sentence: '새로운 프로젝트를 오늘 시작했어요.',
          translation: 'I started a new project today.',
        },
        koreanWords: data.word_info,
        hanjaWords: filteredHanjaWords,
      });

      setLoading(false);
      eventSource.close();
      onDone();
    });

    eventSource.onerror = () => {
      console.error('SSE connection failed.');
      setProgressMessages([
        'Something went wrong while analyzing the input query.',
      ]);
      setLoading(false);
      eventSource.close();
      onDone();
    };

    return () => {
      eventSource.close();
    };
  }, [input]);

  return (
    <div className="w-full space-y-4">
      {loading && (
        <ul className="text-sm text-gray-600 pl-1 space-y-1">
          {progressMessages.map((msg, i) => (
            <li key={i} className="animate-pulse">
              {msg}
            </li>
          ))}
        </ul>
      )}

      {result && <ResultBlock result={result} />}
    </div>
  );
}
