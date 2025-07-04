import { useState } from 'react';
import LanguageAnalyzer from './LanguageAnalyzer';
import YouTubeTranscript from './YouTubeTranscript';

export default function Tabs() {
  const [mode, setMode] = useState<'analyze' | 'search' | 'youtube'>('analyze');
  const [analyzeQuery, setAnalyzeQuery] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [submittedAnalyzeQuery, setSubmittedAnalyzeQuery] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [submittedYoutubeUrl, setSubmittedYoutubeUrl] = useState('');

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    setSubmittedAnalyzeQuery(analyzeQuery.trim());
  };

  return (
    <div className="w-full flex flex-col items-start">
      <div className="w-[645px] space-y-4">
        {/* Tabs */}
        <div className="flex space-x-2">
          <button
            className={`px-4 py-2 rounded-md text-sm font-medium transition ${
              mode === 'analyze'
                ? 'bg-black text-white'
                : 'border border-gray-300 text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setMode('analyze')}
          >
            Language Analysis
          </button>
          <button
            className={`px-4 py-2 rounded-md text-sm font-medium transition ${
              mode === 'youtube'
                ? 'bg-black text-white'
                : 'border border-gray-300 text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setMode('youtube')}
          >
            YouTube Player
          </button>
        </div>

        {/* Input + Button */}
        <div className="flex space-x-2 w-full">
          <input
            value={
              mode === 'analyze'
                ? analyzeQuery
                : mode === 'search'
                  ? searchQuery
                  : youtubeUrl
            }
            onChange={(e) => {
              const val = e.target.value;
              if (mode === 'analyze') setAnalyzeQuery(val);
              else if (mode === 'search') setSearchQuery(val);
              else setYoutubeUrl(val);
            }}
            placeholder={
              mode === 'analyze'
                ? 'Enter Korean word or phrase: 오늘부터 한국어를 배우기 시작하기로 결심했다!'
                : mode === 'search'
                  ? 'Enter a question: Why did he decide to start a brand?'
                  : 'Paste YouTube URL'
            }
            className="flex-grow border border-gray-300 rounded-md px-3 py-2 focus:outline-none"
            type="text"
          />
          {mode === 'analyze' && (
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className={`px-4 py-2 rounded-md text-sm ${
                isAnalyzing ? 'bg-gray-400 text-white' : 'bg-black text-white'
              }`}
            >
              Analyze
            </button>
          )}
          {mode === 'youtube' && (
            <button
              onClick={() => setSubmittedYoutubeUrl(youtubeUrl.trim())}
              className="px-4 py-2 rounded-md text-sm bg-black text-white"
            >
              Load
            </button>
          )}
        </div>

        <div className="space-y-4">
          <div style={{ display: mode === 'analyze' ? 'block' : 'none' }}>
            <LanguageAnalyzer
              input={submittedAnalyzeQuery}
              onDone={() => setIsAnalyzing(false)}
            />
          </div>
          <div style={{ display: mode === 'youtube' ? 'block' : 'none' }}>
            <YouTubeTranscript url={submittedYoutubeUrl} />
          </div>
        </div>
      </div>
    </div>
  );
}
