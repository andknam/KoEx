import { useState } from 'react';
import InputForm from './components/InputForm';
import ResultBlock from './components/ResultBlock';

export default function App() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  //   try {
  //     const response = await fetch(`http://localhost:8000/analyze?word=${encodeURIComponent(input)}`);
  //     const data = await response.json();

  //     // Transform API response into your frontend state shape if necessary
  //     setResult({
  //       koreanDef: data.definition_kr,
  //       englishDef: data.definition_en,
  //       romanized: data.romanized,
  //       example: {
  //         sentence: data.example_sentence,
  //         translation: data.example_translation, // optional, if included
  //       },
  //       characters: data.characters.map((char: any) => ({
  //         char: char.char,
  //         hanja: char.hanja,
  //         pinyin: char.pinyin,
  //         meaning: char.meaning,
  //         strokeGif: char.stroke_order_gif,
  //       })),
  //     });
  //   } catch (err) {
  //     console.error('Error fetching analysis:', err);
  //     // optionally show fallback or error UI
  //   } finally {
  //     setLoading(false);
  //   }
  // };

  const handleSubmit = async () => {
    setLoading(true);

    try {
      console.log(input);
      const response = await fetch(
        `http://localhost:8000/analyze?input=${encodeURIComponent(input)}`
      );
      const data = await response.json();

      console.log(data.words);

      setResult({
        koreanDef: 'placeholder',
        englishDef: 'Start: the act of beginning something',
        romanized: data.romanization,
        example: {
          sentence: '새로운 프로젝트를 오늘 시작했어요.',
          translation: 'I started a new project today.',
        },
        words: data.words
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
