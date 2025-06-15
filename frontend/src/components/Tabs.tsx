import { useState } from 'react';
import LanguageAnalyzer from './LanguageAnalyzer';
import SemanticSearch from './SemanticSearch';

export default function Tabs() {
  const [mode, setMode] = useState<'analyze' | 'search'>('analyze');
  const [analyzeQuery, setAnalyzeQuery] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [submittedAnalyzeQuery, setSubmittedAnalyzeQuery] = useState('');
  const [submittedSearchQuery, setSubmittedSearchQuery] = useState('');
  const [searchTrigger, setSearchTrigger] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    setSubmittedAnalyzeQuery(analyzeQuery.trim());
  };

  const handleSearch = () => {
    setIsSearching(true);
    setSubmittedSearchQuery(searchQuery.trim());
    setSearchTrigger((prev) => prev + 1);
  };

  return (
    <div className="w-full flex flex-col items-start">
      <div className="w-full max-w-3xl space-y-4">
        {/* Tab Buttons */}
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
              mode === 'search'
                ? 'bg-black text-white'
                : 'border border-gray-300 text-gray-700 hover:bg-gray-100'
            }`}
            onClick={() => setMode('search')}
          >
            Semantic Search
          </button>
        </div>

        {/* Input + Button */}
        <div className="flex space-x-2 w-full">
          <input
            value={mode === 'analyze' ? analyzeQuery : searchQuery}
            onChange={(e) =>
              mode === 'analyze'
                ? setAnalyzeQuery(e.target.value)
                : setSearchQuery(e.target.value)
            }
            placeholder={
              mode === 'analyze'
                ? 'Enter Korean word or phrase: 오늘부터 한국어를 배우기 시작하기로 결심했다!'
                : 'Enter a question: Why did he decide to start a brand?'
            }
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black"
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
          {mode === 'search' && (
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className={`px-4 py-2 rounded-md text-sm ${
                isSearching ? 'bg-gray-400 text-white' : 'bg-black text-white'
              }`}
            >
              Search
            </button>
          )}
        </div>

        {/* Results (keep both components mounted) */}
        <div className="space-y-4">
          <div style={{ display: mode === 'analyze' ? 'block' : 'none' }}>
            <LanguageAnalyzer
              input={submittedAnalyzeQuery}
              onDone={() => setIsAnalyzing(false)}
            />
          </div>
          <div style={{ display: mode === 'search' ? 'block' : 'none' }}>
            <SemanticSearch
              input={submittedSearchQuery}
              trigger={searchTrigger}
              onDone={() => setIsSearching(false)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
