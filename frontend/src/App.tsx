import { useState, useRef, useCallback } from 'react';
import InputForm from './components/InputForm';
import ResultBlock from './components/ResultBlock';

export default function App() {
  const inputRef = useRef<HTMLInputElement>(null); // useRef instead of useState
  const [loading, setLoading] = useState(false);
  const [progressMessages, setProgressMessages] = useState<string[]>([]);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = useCallback(() => {
    const input = inputRef.current?.value ?? '';
    if (!input.trim()) return;

    setLoading(true);
    setProgressMessages([]);
    setResult(null);

    const eventSource = new EventSource(
      `http://localhost:8000/analyze-stream?input=${encodeURIComponent(input)}`
    );

    eventSource.addEventListener('progress', (event: MessageEvent) => {
      setProgressMessages((prev) => [...prev, event.data]);
    });

    eventSource.addEventListener('result', (event: MessageEvent) => {
      const data = JSON.parse(event.data);

      console.log(data);

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

      if (inputRef.current) inputRef.current.value = ''; // clear manually
      setLoading(false);
      eventSource.close();
    });

    eventSource.onerror = () => {
      console.error('SSE connection failed.');
      setProgressMessages([
        'Something went wrong while analyzing the input query.',
      ]);
      setLoading(false);
      eventSource.close();
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
      <h1 className="text-3xl font-bold mb-4">KoEx</h1>

      <InputForm inputRef={inputRef} onSubmit={handleSubmit} />

      {loading && (
        <ul className="text-sm text-gray-600 mb-4 space-y-1">
          {progressMessages.map((msg, i) => (
            <li key={i} className="animate-pulse">{msg}</li>
          ))}
        </ul>
      )}

      {result && <ResultBlock result={result} />}
    </div>
  );
}