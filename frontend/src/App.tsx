import { useState } from 'react';
import InputForm from './components/InputForm';
import ResultBlock from './components/ResultBlock';

export default function App() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async () => {
    setLoading(true);

    try {
      console.log(input);
      const response = await fetch(
        `http://localhost:8000/analyze?input=${encodeURIComponent(input)}`
      );
      const data = await response.json();

      const filteredHanjaWords = data.hanja_words.filter(
        (item) => item.hanja && item.characters && item.characters.length > 0
      );

      console.log(data);

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
    } catch (err) {
      console.error('Error fetching analysis:', err);
      // optionally show fallback or error UI
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
      <h1 className="text-3xl font-bold mb-4">KoEx</h1>

      <InputForm input={input} setInput={setInput} onSubmit={handleSubmit} />

      {loading && <p>Loading...</p>}

      {result && <ResultBlock result={result} />}
    </div>
  );
}
